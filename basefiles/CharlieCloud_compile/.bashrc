# .bashrc

#test if interactive shell
STR="$-"
SUB="i"
INTERACTIVE=0
if [[ "$STR" == *"$SUB"* ]]; then
    INTERACTIVE=1
fi


# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi
function git_ps1 ()
{
	local g="$(git rev-parse --git-dir 2>/dev/null)"
	if [ -n "$g" ]; then
		if [ -d "$g/rebase-apply" ]
		then
			if test -f "$g/rebase-apply/rebasing"
			then
				r="|REBASE"
			elif test -f "$g/rebase-apply/applying"
			then
				r="|AM"
			else
				r="|AM/REBASE"
			fi
			b="$(git symbolic-ref HEAD 2>/dev/null)"
		elif [ -f "$g/rebase-merge/interactive" ]
		then
			r="|REBASE-i"
			b="$(cat "$g/rebase-merge/head-name")"
		elif [ -d "$g/rebase-merge" ]
		then
			r="|REBASE-m"
			b="$(cat "$g/rebase-merge/head-name")"
		elif [ -f "$g/MERGE_HEAD" ]
		then
			r="|MERGING"
			b="$(git symbolic-ref HEAD 2>/dev/null)"
		else
			if [ -f "$g/BISECT_LOG" ]
			then
				r="|BISECTING"
			fi
			if ! b="$(git symbolic-ref HEAD 2>/dev/null)"
			then
				if ! b="$(git describe --exact-match HEAD 2>/dev/null)"
				then
					b="$(cut -c1-7 "$g/HEAD")..."
				fi
			fi
		fi

		if [ -n "${1-}" ]; then
			printf "$1" "${b##refs/heads/}$r"
		else
			printf " (%s)" "${b##refs/heads/}$r"
		fi
    else
        r="";
	fi
}
# User specific environment
source ~/.updir.sh
source ~/.dirB.sh


export HOME=/home/sim
PATH="$HOME/.local/bin:$HOME/go/bin:$HOME/simulator/Install/bin:$HOME/simulator/python_env/bin:$PATH"
export PATH
export LD_LIBRARY_PATH=/usr/local/lib64/:/usr/local/lib/:$HOME/simulator/Install/lib:$HOME/simulator/Install/lib64:$LD_LIBRARY_PATH
function do_binds()
{
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
}
if [[ $INTERACTIVE -eq 1 ]]
then
do_binds
fi

prompt_color="48;5;78"
export PS1="\$(git_ps1)\[$(tput setab 0)$(tput setaf 7)\]\[\e[${prompt_color};1;30m\]\u: \w>\[$(tput sgr0)\]\[\e[0m\] "
# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions
