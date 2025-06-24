#linbox-fox
用afei修改项目:linbox对其进行一定程度的压缩和删减，同时做一些个人优化

下载所有文件，放在/SD card/目录下，termux执行foxbox.sh文件，然后就可以一键安装了

proot的用户密码是2580，默认不输入密码

如果要在普通ternux使用，请执行
apt remove termux-x11-nightly -y
  pkg update -y 
  pkg install x11-repo -y
  pkg install root-repo -y
  pkg install termux-x11-nightly -y
这是必要的过程，因为我更多使用云佬整合终端