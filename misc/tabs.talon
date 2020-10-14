tag: user.tabs
-
tab (open | new): app.tab_open()
tab previous: app.tab_previous()
tab move previous: key(ctrl-shift-pgup)
tab move next: key(ctrl-shift-pgdown)
tab next: app.tab_next()
tab close: app.tab_close()
tab reopen: app.tab_reopen()
go tab <number>: user.tab_jump(number)
go tab final: user.tab_final()