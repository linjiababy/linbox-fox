#!/bin/bash

RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
PURPLE='\033[1;35m'
CYAN='\033[1;36m'
NC='\033[0m'
BOLD='\033[1m'
UNDERLINE='\033[4m'

function progress_bar {
    local duration=${1}
    local width=50
    local increment=$((100/width))
    for ((i=0; i<=width; i++)); do
        percentage=$((i * increment))
        filled=$(printf "%-${i}s" "")
        empty=$(printf "%-$((width-i))s" "")
        printf "\r[${PURPLE}%-${width}s${NC}] ${CYAN}%3d%%${NC}" "${filled// /█}" "${percentage}"
        sleep "$duration"
    done
    printf "\n"
}

function show_step {
    echo -e "\n${PURPLE}▶ ${BOLD}${UNDERLINE}步骤 $1/$2${NC} - ${CYAN}$3${NC}\n"
}

function check_file {
    if [ ! -f "$1" ]; then
        echo -e "${RED}错误：文件 $1 不存在！${NC}"
        exit 1
    fi
}

function check_extract_path {
    if [ ! -d "$1" ]; then
        echo -e "${RED}错误：解压路径 $1 不存在！${NC}"
        exit 1
    fi
}

function extract_file {
    local src=$1
    local dest=$2
    echo -e "${YELLOW}正在解压 $src 到 $dest...${NC}"
    if tar -zxf "$src" -C "$dest" &>/dev/null; then
        echo -e "${GREEN}✓ 解压成功${NC}"
    else
        echo -e "${RED}错误：解压失败！请检查文件是否损坏或路径是否正确。${NC}"
        exit 1
    fi
}

function show_banner {
    clear
    echo -e "\033[1;36m"  # 青色
    echo ' ███████╗ ██████╗ ██╗  ██╗ ██████╗ ███████╗'
    echo ' ██╔════╝██╔═══██╗╚██╗██╔╝██╔═══██╗██╔════╝'
    echo ' █████╗  ██║   ██║ ╚███╔╝ ██║   ██║███████╗'
    echo -e "\033[1;35m"  # 紫色
    echo ' ██╔══╝  ██║   ██║ ██╔██╗ ██║   ██║╚════██║'
    echo ' ██║     ╚██████╔╝██╔╝ ██╗╚██████╔╝███████║'
    echo ' ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝'
    echo -e "\033[1;33m"  # 金色
    echo '════════════════ 极速图形化系统 ════════════════'
    echo -e "${NC}"
}

total_steps=7
current_step=1
show_banner

show_step $current_step $total_steps "恢复x11环境"
check_file "/sdcard/termux.tar.gz"
check_extract_path "/data/data/com.termux/files"
extract_file "/sdcard/termux.tar.gz" "/data/data/com.termux/files"
((current_step++))

show_step $current_step $total_steps "安装glibc核心组件"
check_file "/sdcard/glibc.tar.gz"
check_extract_path "/data/data/com.termux/files"
extract_file "/sdcard/glibc.tar.gz" "/data/data/com.termux/files"
((current_step++))

show_step $current_step $total_steps "DarkOS解码模块安装"
echo -e "${BOLD}是否需要安装DarkOS解码支持? (${GREEN}y${NC}/${RED}n${NC})${NC}"
read -r -n 1 -t 15 user_input
echo
if [[ "$user_input" =~ [yY] ]]; then
    check_file "/sdcard/lib.tar.gz"
    check_extract_path "/data/data/com.termux/files/usr/glibc/"
    extract_file "/sdcard/lib.tar.gz" "/data/data/com.termux/files/usr/glibc/"
else
    echo -e "${YELLOW}⚠ 已跳过解码模块安装${NC}"
fi
((current_step++))

show_step $current_step $total_steps "系统权限配置"
echo -e "${YELLOW}正在设置安全权限...${NC}"
chmod a+x $PREFIX/bin/startonwine $PREFIX/bin/stopwine $PREFIX/bin/wine_menu $PREFIX/bin/starttfmpt $PREFIX/bin/starttfmpt1
progress_bar 0.01
echo -e "${GREEN}✓ 权限配置完成${NC}"
((current_step++))

show_step $current_step $total_steps "系统自动修复"
echo -e "${BOLD}按回车开始系统修复 (10秒后自动继续)...${NC}"
read -r -t 10
echo -e "\n${YELLOW}修复SSH服务...${NC}"
pkg i openssh -y &>/dev/null &
progress_bar 0.03
echo -e "\n${YELLOW}修复Debian用户配置...${NC}"
proot-distro login debian --shared-tmp -- /bin/bash -c 'export PULSE_SERVER=127.0.0.1 && export XDG_RUNTIME_DIR=${TMPDIR} && su - root -c "env DISPLAY=:0 dpkg --configure -a"' &>/dev/null &
progress_bar 0.05
proot-distro login debian --shared-tmp -- /bin/bash -c 'export PULSE_SERVER=127.0.0.1 && export XDG_RUNTIME_DIR=${TMPDIR} && su - root -c "env DISPLAY=:0 apt reinstall sudo -y"' &>/dev/null &
progress_bar 0.04
echo -e "${GREEN}✓ 系统修复完成${NC}"
((current_step++))

show_step $current_step $total_steps "安装完成"
echo -e "${GREEN}=============================================="
echo -e " ███████╗ ██████╗ ██╗  ██╗ ██████╗ ███████╗"
echo -e " ██╔════╝██╔═══██╗╚██╗██╔╝██╔═══██╗██╔════╝"
echo -e " █████╗  ██║   ██║ ╚███╔╝ ██║   ██║███████╗"
echo -e " ██╔══╝  ██║   ██║ ██╔██╗ ██║   ██║╚════██║"
echo -e " ██║     ╚██████╔╝██╔╝ ██╗╚██████╔╝███████║"
echo -e " ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝"
echo -e "==============================================${NC}"
echo -e "${BOLD}使用说明："
echo -e "${YELLOW}▶ 启动命令: ${GREEN}foxos${NC}"
echo -e "${YELLOW}▶ 文件管理: 桌面双击 ${GREEN}Wine菜单${NC}"
echo -e "${YELLOW}▶ 技术支持: ${CYAN}https://foxos.support${NC}"
echo -e "${YELLOW}▶ 问题反馈: ${CYAN}feedback@foxos.com${NC}"
echo -e "\n${RED}请杀后台后重新进入系统以应用所有更改！${NC}"

echo -e "\n${GREEN}安装已完成！感谢您使用 foxos 系统！${NC}"
exit 0