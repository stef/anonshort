unshorten='http://seeks.hsbp.org:8080/?u='

function unshorten() {
    url="$(echo "$1" | /bin/egrep -o 'https?://\S*')"
    [[ -z "$url" ]] && return
    short="$(curl "$unshorten$url")"
    [[ "$url" == "$short" ]] && return
    print "$short"
}

while read line; do
    unshorten "$line"
done
