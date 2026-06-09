#!/bin/bash
# foxbox模拟器安装脚本
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
PURPLE='\033[1;35m'
CYAN='\033[1;36m'
NC='\033[0m'
BOLD='\033[1m'
UNDERLINE='\033[4m'

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
    if tar -Jxf "$src" -C "$dest" &>/dev/null; then
        echo -e "${GREEN}✓ 解压成功${NC}"
    else
        echo -e "${RED}错误：解压失败！请检查文件是否损坏或路径是否正确。${NC}"
        exit 1
    fi
}

function show_banner {
    clear
    echo -e "\e[38;5;27m███████╗ ██████╗ ██╗  ██╗██████╗  ██████╗ ██╗  ██╗"
    echo -e "\e[38;5;27m██╔════╝██╔═══██╗╚██╗██╔╝██╔══██╗██╔═══██╗╚██╗██╔╝"
    echo -e "\e[38;5;27m█████╗  ██║   ██║ ╚███╔╝ ██████╔╝██║   ██║ ╚███╔╝"
    echo -e "\e[38;5;45m██╔══╝  ██║   ██║ ██╔██╗ ██╔══██╗██║   ██║ ██╔██╗"
    echo -e "\e[38;5;45m██║     ╚██████╔╝██╔╝ ██╗██████╔╝╚██████╔╝██╔╝ ██╗"
    echo -e "\e[38;5;45m╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝\e[0m"
    echo -e "\033[1;33m═════════════════ FOXBOX 系统 ═════════════════${NC}"
    echo -e "${CYAN}本仿真器由b站狐尼克的梦构建，在此感谢所有对我有所帮助的人${NC}"
    echo -e "${YELLOW}Afei,Asai,waim908,Deemo,小白一枚，莫泽，咔咔龙，hostei等大佬帮助${NC}"
    echo -e "${GREEN}感谢mobox开发人员，感谢所有对模拟器付出的人${NC}"
    echo
}

total_steps=7
current_step=1
show_banner

# --- 新增步骤1: 处理器选择 ---
show_step $current_step $total_steps "请选择你的处理器类型"
echo -e "${YELLOW}请选择你的处理器：${NC}"
echo -e "  ${GREEN}1${NC}) 高通骁龙"
echo -e "  ${GREEN}2${NC}) 天玑或其它"
echo -e "\n${CYAN}提示：若10秒内无输入，将默认选择【2. 天玑或其它】${NC}"
read -r -t 10 -p "请输入选项 (1 或 2): " processor_choice

# 处理默认值 (超时或空输入)
if [ -z "$processor_choice" ]; then
    processor_choice="2"
    echo -e "\n${YELLOW}超时未选择，已自动选择: 2) 天玑或其它${NC}"
elif [ "$processor_choice" != "1" ] && [ "$processor_choice" != "2" ]; then
    echo -e "\n${YELLOW}无效输入，自动使用默认选项: 2) 天玑或其它${NC}"
    processor_choice="2"
fi

echo -e "${GREEN}✓ 当前选择: $([ "$processor_choice" == "1" ] && echo "高通骁龙" || echo "天玑或其它")${NC}"
sleep 1
((current_step++))

# --- 原步骤1 (现步骤2): 恢复x11环境 ---
show_step $current_step $total_steps "恢复x11环境"
check_file "/sdcard/termux.tar.xz"
check_extract_path "/data/data/com.termux/files"
tar -C "/data/data/com.termux/files" -Jxf "/sdcard/termux.tar.xz" &>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 解压成功${NC}"
else
    echo -e "${RED}错误：解压失败！请检查文件是否损坏或路径是否正确。${NC}"
    exit 1
fi
((current_step++))

# --- 原步骤2 (现步骤3): 安装Debian环境 ---
show_step $current_step $total_steps "安装Debian环境"
check_file "/sdcard/debian.tar.xz"
check_extract_path "/data/data/com.termux/files"
tar -C "/data/data/com.termux/files" -Jxf "/sdcard/debian.tar.xz" &>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 解压成功${NC}"
else
    echo -e "${RED}错误：解压失败！请检查文件是否损坏或路径是否正确。${NC}"
    exit 1
fi
((current_step++))

# --- 原步骤3 (现步骤4): 安装glibc核心组件 ---
show_step $current_step $total_steps "安装glibc核心组件"
check_file "/sdcard/glibc.tar.xz"
check_extract_path "/data/data/com.termux/files"
tar -C "/data/data/com.termux/files" -Jxf "/sdcard/glibc.tar.xz" &>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 解压成功${NC}"
else
    echo -e "${RED}错误：解压失败！请检查文件是否损坏或路径是否正确。${NC}"
    exit 1
fi
((current_step++))

# --- 原步骤4 (现步骤5): 系统权限配置 ---
show_step $current_step $total_steps "系统权限配置"
echo -e "${YELLOW}正在设置安全权限...${NC}"
chmod a+x $PREFIX/bin/startonwine $PREFIX/bin/stopwine $PREFIX/bin/wine_menu.py $PREFIX/bin/app.py
echo -e "${GREEN}✓ 权限配置完成${NC}"
((current_step++))

# --- 原步骤5 (现步骤6): 系统自动修复 (包含针对处理器选项的修改) ---
show_step $current_step $total_steps "系统自动修复"
echo -e "${BOLD}按回车开始系统修复 (10秒后自动继续)...${NC}"
read -r -t 10

echo -e "\n${YELLOW}安装SSH服务...${NC}"
pkg reinstall openssh -y
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ SSH安装成功${NC}"
else
    echo -e "${RED}✗ SSH安装失败${NC}"
fi

echo -e "\n${YELLOW}修复Debian用户配置...${NC}"

proot-distro login debian --shared-tmp -- /bin/bash -c 'apt-get update && apt-get reinstall sudo -y'
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ sudo安装成功${NC}"
    proot-distro login debian --shared-tmp -- /bin/bash -c 'echo "user ALL=(ALL:ALL) ALL" >> /etc/sudoers'
    echo -e "${GREEN}✓ sudo配置完成${NC}"
else
    echo -e "${RED}✗ sudo安装失败${NC}"
fi

proot-distro login debian --shared-tmp -- /bin/bash -c 'dpkg --configure -a'
echo -e "${GREEN}✓ Debian包修复完成${NC}"

# --- 新增: 如果是天玑或其它(选项2)，则注释掉 .profile 中的 export 行 ---
if [ "$processor_choice" == "2" ]; then
    echo -e "\n${YELLOW}检测到天玑或其它处理器，正在调整环境变量配置...${NC}"
    proot-distro login debian --shared-tmp -- /bin/bash -c '
        PROFILE_PATH="/home/fox/.profile"
        if [ -f "$PROFILE_PATH" ]; then
            # 备份原文件
            cp "$PROFILE_PATH" "${PROFILE_PATH}.bak"
            # 注释掉以 export 开头的行
            sed -i "s/^export/#export/" "$PROFILE_PATH"
            echo -e "${GREEN}✓ 已注释 $PROFILE_PATH 中的 export 行${NC}"
            echo -e "${YELLOW}  备份文件保存为: ${PROFILE_PATH}.bak${NC}"
        else
            echo -e "${RED}✗ 警告: $PROFILE_PATH 不存在，跳过修改${NC}"
        fi
    '
    # 注意：上面的echo中使用了颜色代码，但在proot里可能不解析；为了清晰，保留原样，实际输出可能无颜色。
    # 为了proot内正确显示，可简化，但不影响功能。
    echo -e "${GREEN}✓ 针对天玑/其它处理器的环境优化已完成${NC}"
else
    echo -e "\n${GREEN}✓ 检测到高通骁龙处理器，保持原环境配置不变${NC}"
fi

echo -e "${GREEN}✓ 系统修复完成${NC}"
((current_step++))

# --- 原步骤6 (现步骤7): 安装完成 ---
show_step $current_step $total_steps "安装完成"
echo -e "\e[38;5;27m███████╗ ██████╗ ██╗  ██╗██████╗  ██████╗ ██╗  ██╗"
echo -e "\e[38;5;27m██╔════╝██╔═══██╗╚██╗██╔╝██╔══██╗██╔═══██╗╚██╗██╔╝"
echo -e "\e[38;5;27m█████╗  ██║   ██║ ╚███╔╝ ██████╔╝██║   ██║ ╚███╔╝"
echo -e "\e[38;5;45m██╔══╝  ██║   ██║ ██╔██╗ ██╔══██╗██║   ██║ ██╔██╗"
echo -e "\e[38;5;45m██║     ╚██████╔╝██╔╝ ██╗██████╔╝╚██████╔╝██╔╝ ██╗"
echo -e "\e[38;5;45m╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝\e[0m"
echo -e "${BOLD}使用说明："
echo -e "${YELLOW}▶ 启动命令: ${GREEN}Foxbox${NC}"
echo -e "${YELLOW}▶ 文件管理: 桌面双击 ${GREEN}Wine菜单${NC}"
echo -e "${YELLOW}▶ 技术支持: ${CYAN}https://foxbox.com${NC}"
echo -e "${YELLOW}▶ 问题反馈: ${CYAN}QQ：837746893${NC}"
echo -e "\n${RED}请杀后台后重新进入系统以应用所有更改！${NC}"

echo -e "\n${GREEN}安装已完成！感谢您使用 FOXBOX 系统！${NC}"
exit 0