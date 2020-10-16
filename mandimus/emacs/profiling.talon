os: linux
app: emacs
-

profiler start: user.minibuffer("profiler-start")
profiler stop: user.minibuffer("profiler-stop")
profiler report: user.minibuffer("profiler-report")
instrument function: user.minibuffer("elp-instrument-function")
instrument results: user.minibuffer("elp-restore-function")
instrument master: user.minibuffer("elp-set-master")
instrument package: user.minibuffer("elp-instrument-package")
macro expand: user.minibuffer("macroexpand-point")
