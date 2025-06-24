#!/bin/bash
# 定义颜色和样式
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
PURPLE='\033[1;35m'
CYAN='\033[1;36m'
NC='\033[0m'
BOLD='\033[1m'
UNDERLINE='\033[4m'

# 简单循环进度条
function progress_bar {
    local duration=${1}
    local width=20
    for ((i=0; i<=width; i++)); do
        printf "\r[${PURPLE}%-${width}s${NC}]" "${BOLD}${PURPLE}▓${NC}${PURPLE}▓${NC}${PURPLE}▓${NC}${PURPLE}▓${NC}${PURPLE}▓${NC}"
        sleep "$duration"
    done
    printf "\n"
}

# 显示步骤标题
function show_step {
    echo -e "\n${PURPLE}▶ ${BOLD}${UNDERLINE}步骤 $1/$2${NC} - ${CYAN}$3${NC}\n"
}

# 检查文件是否存在
function check_file {
    if [ ! -f "$1" ]; then
        echo -e "${RED}错误：文件 $1 不存在！${NC}"
        exit 1
    fi
}

# 检查解压路径是否存在
function check_extract_path {
    if [ ! -d "$1" ]; then
        echo -e "${RED}错误：解压路径 $1 不存在！${NC}"
        exit 1
    fi
}

# 解压文件（使用xz格式）
function extract_file {
    local src=$1
    local dest=$2
    echo -e "${YELLOW}正在解压 $src 到 $dest...${NC}"
    if tar -Jxf "$src" -C "$dest" &>/dev/null; then
        echo -e "${GREEN}✓ 解压成功${NC}"
    else
        echo -e "${RED}错误：解压失败！请检查文件是否损坏或路径是否正确。${NC}"
        exit 1
    fi
}

# ASCII艺术字 - 完全按照用户提供的样式
function show_banner {
    clear
    echo -e "\e[38;5;27m███████╗ ██████╗ ██╗  ██╗██████╗  ██████╗ ██╗  ██╗"
    echo -e "\e[38;5;27m██╔════╝██╔═══██╗╚██╗██╔╝██╔══██╗██╔═══██╗╚██╗██╔╝"
    echo -e "\e[38;5;27m█████╗  ██║   ██║ ╚███╔╝ ██████╔╝██║   ██║ ╚███╔╝"
    echo -e "\e[38;5;45m██╔══╝  ██║   ██║ ██╔██╗ ██╔══██╗██║   ██║ ██╔██╗"
    echo -e "\e[38;5;45m██║     ╚██████╔╝██╔╝ ██╗██████╔╝╚██████╔╝██╔╝ ██╗"
    echo -e "\e[38;5;45m╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝\e[0m"
    echo -e "\033[1;33m═════════════════ FOXBOX 系统 ═════════════════${NC}"
}

# 初始化安装
total_steps=8
current_step=1
show_banner

# 步骤1：恢复x11环境
show_step $current_step $total_steps "恢复x11环境"
check_file "/sdcard/termux.tar.xz"
check_extract_path "/data/data/com.termux/files"
extract_file "/sdcard/termux.tar.xz" "/data/data/com.termux/files"
((current_step++))

# 步骤2：安装Debian环境
show_step $current_step $total_steps "安装Debian环境"
check_file "/sdcard/debian.tar.xz"
check_extract_path "/data/data/com.termux/files"
extract_file "/sdcard/debian.tar.xz" "/data/data/com.termux/files"
((current_step++))

# 步骤3：安装glibc本体
show_step $current_step $total_steps "安装glibc核心组件"
check_file "/sdcard/glibc.tar.xz"
check_extract_path "/data/data/com.termux/files"
extract_file "/sdcard/glibc.tar.xz" "/data/data/com.termux/files"
((current_step++))

# 步骤4：DarkOS解码恢复
show_step $current_step $total_steps "DarkOS解码模块安装"
echo -e "${BOLD}是否需要安装DarkOS解码支持? (${GREEN}y${NC}/${RED}n${NC})${NC}"
read -r -n 1 -t 15 user_input
echo
if [[ "$user_input" =~ [yY] ]]; then
    check_file "/sdcard/lib.tar.gz"  # 修改为检查tar.gz文件
    check_extract_path "/data/data/com.termux/files/usr/glibc/"
    echo -e "${YELLOW}正在解压 lib.tar.gz 到 /data/data/com.termux/files/usr/glibc/...${NC}"
    if tar -zxf "/sdcard/lib.tar.gz" -C "/data/data/com.termux/files/usr/glibc/" &>/dev/null; then
        echo -e "${GREEN}✓ 解压成功${NC}"
    else
        echo -e "${RED}错误：解压失败！请检查文件是否损坏或路径是否正确。${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ 已跳过解码模块安装${NC}"
fi
((current_step++))

# 步骤5：权限配置
show_step $current_step $total_steps "系统权限配置"
echo -e "${YELLOW}正在设置安全权限...${NC}"
chmod a+x $PREFIX/bin/startonwine $PREFIX/bin/stopwine $PREFIX/bin/wine_menu.py $PREFIX/bin/start-wfm $PREFIX/bin/app.py
progress_bar 0.01
echo -e "${GREEN}✓ 权限配置完成${NC}"
((current_step++))

# 步骤6：系统修复 - 修复后的部分
show_step $current_step $total_steps "系统自动修复"
echo -e "${BOLD}按回车开始系统修复 (10秒后自动继续)...${NC}"
read -r -t 10

echo -e "\n${YELLOW}安装SSH服务...${NC}"
pkg install openssh -y
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ SSH安装成功${NC}"
else
    echo -e "${RED}✗ SSH安装失败${NC}"
fi
progress_bar 0.03

echo -e "\n${YELLOW}修复Debian用户配置...${NC}"
# 在Termux环境中安装proot-distro
pkg install proot-distro -y
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ proot-distro安装成功${NC}"
    
    # 在Debian环境中安装sudo
    proot-distro login debian --shared-tmp -- /bin/bash -c 'apt-get update && apt-get reinstall sudo -y'
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ sudo安装成功${NC}"
        
        # 配置sudo
        proot-distro login debian --shared-tmp -- /bin/bash -c 'echo "user ALL=(ALL:ALL) ALL" >> /etc/sudoers'
        echo -e "${GREEN}✓ sudo配置完成${NC}"
    else
        echo -e "${RED}✗ sudo安装失败${NC}"
    fi
    
    # 修复Debian包
    proot-distro login debian --shared-tmp -- /bin/bash -c 'dpkg --configure -a'
    echo -e "${GREEN}✓ Debian包修复完成${NC}"
else
    echo -e "${RED}✗ proot-distro安装失败${NC}"
fi
progress_bar 0.05

echo -e "${GREEN}✓ 系统修复完成${NC}"
((current_step++))

# 步骤7：安装完成
show_step $current_step $total_steps "安装完成"
echo -e "\e[38;5;27m███████╗ ██████╗ ██╗  ██╗██████╗  ██████╗ ██╗  ██╗"
echo -e "\e[38;5;27m██╔════╝██╔═══██╗╚██╗██╔╝██╔══██╗██╔═══██╗╚██╗██╔╝"
echo -e "\e[38;5;27m█████╗  ██║   ██║ ╚███╔╝ ██████╔╝██║   ██║ ╚███╔╝"
echo -e "\e[38;5;45m██╔══╝  ██║   ██║ ██╔██╗ ██╔══██╗██║   ██║ ██╔██╗"
echo -e "\e[38;5;45m██║     ╚██████╔╝██╔╝ ██╗██████╔╝╚██████╔╝██╔╝ ██╗"
echo -e "\e[38;5;45m╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝\e[0m"
echo -e "${BOLD}使用说明："
echo -e "${YELLOW}▶ 启动命令: ${GREEN}foxbox${NC}"
echo -e "${YELLOW}▶ 文件管理: 桌面双击 ${GREEN}Wine菜单${NC}"
echo -e "${YELLOW}▶ 技术支持: ${CYAN}https://foxbox.com${NC}"
echo -e "${YELLOW}▶ 问题反馈: ${CYAN}support@foxbox.com${NC}"
echo -e "\n${RED}请杀后台后重新进入系统以应用所有更改！${NC}"

# 步骤8：退出脚本
echo -e "\n${GREEN}安装已完成！感谢您使用 FOXBOX 系统！${NC}"
exit 0