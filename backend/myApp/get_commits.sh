echo '['
git rev-list HEAD | while read sha1; do
    # full_diff="$(git show --format='' $sha1 | sed 's/\"/\\\"/g' | awk '{printf "%s\\n", $0}')"
    commit_log="$(git show --format='%s' -s $sha1 | sed 's/\"//g;s/\\//g' | sed 's/\x00/[NUL]/g;s/\x01/[SOH]/g;s/\x02/[STX]/g;s/\x03/[ETX]/g;s/\x04/[EOT]/g;s/\x05/[ENQ]/g;s/\x06/[ACK]/g;s/\x07/[BEL]/g;s/\x08/[BS]/g;s/\x0A/[LF]/g;s/\x0B/[VT]/g;s/\x0C/[FF]/g;s/\x0D/[CR]/g;s/\x0E/[SO]/g;s/\x0F/[SI]/g;s/\x10/[DLE]/g;s/\x11/[DC1]/g;s/\x12/[DC2]/g;s/\x13/[DC3]/g;s/\x14/[DC4]/g;s/\x15/[NAK]/g;s/\x16/[SYN]/g;s/\x17/[ETB]/g;s/\x18/[CAN]/g;s/\x19/[EM]/g;s/\x1A/[SUB]/g;s/\x1B/[ESC]/g;s/\x1C/[FS]/g;s/\x1D/[GS]/g;s/\x1E/[RS]/g;s/\x1F/[US]/g;s/\x7F/[DEL]/g')"
    git --no-pager show --format="{%n  \"commithash\": \"%H\",%n  \"author\": \"%an\",%n \"authorEmail\": \"%ae\",%n  \"commitTime\": \"%ad\",%n  \"commitMessage\": \"$commit_log\"%n}," -s $sha1
    done
echo ']'
