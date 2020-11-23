os: linux
app: emacs
-

buff <user.buffer_name>$: user.switch_buffer(buffer_name)
last buff: user.switch_last_buffer()

folder <user.folder_name>$: user.switch_folder(folder_name)
last folder: user.switch_last_folder()

channel <user.channel_name>$: user.switch_channel(channel_name)
last channel: user.switch_last_channel()

shell <user.shell_name>$: user.switch_shell(shell_name)
last shell: user.switch_last_shell()

e shell <user.eshell_name>$: user.switch_eshell(eshell_name)
last e shell: user.switch_last_eshell()

special <user.special_name>$: user.switch_special(special_name)
last special: user.switch_last_special()
