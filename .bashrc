# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# User specific environment
PATH="$HOME/.local/bin:$HOME/bin:/$HOME/go/bin:$PATH"
export PATH
export LD_LIBRARY_PATH=/usr/local/lib64/:/usr/local/lib/:$LD_LIBRARY_PATH
bind '"\eu":previous-history'
bind '"\em":next-history'
bind '"\ey":history-search-backward'
bind '"\en":history-search-forward'
bind '"\ej":backward-char'
bind '"\ek":forward-char'
bind '"\eh":unix-line-discard'
bind '"\el":beginning-of-line'
bind '"\e;":end-of-line'
bind '"\ep":yank'
bind '"\eg":kill-line'

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions
