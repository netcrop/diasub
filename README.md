# Diasub
Diasub is a subtitle creation, conversion scripts written in python

## Install, maintain and uninstall
* For linux/unix system:  
```
required commands and packages:
Bash version 4.4+
Python 3+
>
> cd diasub 
> source diasub.sh
> diasub.py.install
```
## Using diasub
```

> cat misc/samplesource.srt
1
02:28:23,766 --> 02:28:26,060
Because if a machine, a robot,

2
02:28:26,394 --> 02:28:28,855
can learn the value of human life,

3
02:28:29,314 --> 02:28:32,025
maybe we can too.
> # Filter out language from subrip text file and replace words defined by dictionary file.
> diasub -o misc/samplesource.srt misc/sampledictionary > untranslated.txt
> cat untranslated.txt
1 Because if a machine, a 654321,
2 can learn the value of 654322 life,
3 maybe we can too.
>
> ... # Human/Machine translation => misc/sampletarget
> cat misc/sampletarget
1 因为如果连一部机器,654321,
2 都学会珍惜654322生命的价值，
3 也许我们也可以。 
>
> # Create translated subrip text file based on 
> # human/machine translated file and dictionary file
> diasub -i misc/samplesource.srt misc/sampledictionary misc/sampletarget > translated.srt
> cat translated.srt
1
02:28:23,766 --> 02:28:26,060
因为如果连一部机器,机器人

2
02:28:26,394 --> 02:28:28,855
都学会珍惜人类生命的价值，

3
02:28:29,314 --> 02:28:32,025
也许我们也可以。
>
> # Delay the entire subtitle by a user defined time
> diasub -shift misc/samplesource.srt 00:00:01:12,00,- > delayed.srt 
> cat delayed.srt
1
02:27:11,766 --> 02:27:14,060
Because if a machine, a robot,

2
02:27:14,394 --> 02:27:16,855
can learn the value of human life,

3
02:27:17,314 --> 02:27:20,025
maybe we can too.
```
## For developers
```
```
## Reporting a bug and security issues

github.com/netcrop/diasub/pulls

## License

[GNU General Public License version 2 (GPLv2)](https://github.com/netcrop/conagent/blob/master/LICENSE)
