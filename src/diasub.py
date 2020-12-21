#!/bin/env -S PATH=/usr/local/bin:/usr/bin python3 -I
import re,tempfile,resource,glob,io,subprocess,sys
import os,socket,getpass,random,datetime,string,operator
class Diasub:
    def __init__(self,*argv):
        self.message = {'-h':' print this help message.',
        '-o':' [subrip text file] [dictionary file]\
        @Filter out original language before translation',
        '-i':' [subrip text file] [dictionary file]\
        @[target language file after translation]\
        @Create translated subrip text file',
        '-ass':'[subrip text file/srt] convert srt to ass',
        '-srt':'[ass file] convert ass to srt',
        '-shift':'[subrip text file/srt] [time shift e.g: 00:01:12,123,-]\
        @Shift time forward/backward' }
        self.argv = argv
        self.args = argv[0]
        self.argc = len(self.args)
        if self.argc == 1: self.usage()
        self.option = { '-h':self.usage ,'-o':self.pretranslate,'-i':self.posttranslate,
        '-ass':self.ass, '-srt':self.srt, '-codec':self.codec, '-time':self.timing,
        '-shift':self.timeshift }
        self.fsep = '\n'
        self.keytype = 'rsa'
        self.hostname = socket.gethostname()
        self.uid = os.getuid()
        self.username = getpass.getuser()
        self.userhost = self.username + self.fsep + self.hostname
        self.homedir = os.environ.get('HOME') + '/'
        self.sshdir = self.homedir + '.ssh/'
        self.tmpdir = '/var/tmp/'
        self.curtty = ''
        self.dicindex = 654321
        self.debugging = DEBUGGING
        self.allcodec = {'ISO-8859':'iso-8859-1','UTF-8':'utf-8'}
        self.operator = {'+':operator.add, '-':operator.sub}
        self.scriptinfo = """[Script Info]
        ; Script by Diasub
        ScriptType: v4.00+
        WrapStyle: 0
        ScaledBorderAndShadow: yes
        YCbCr Matrix: None
        [V4+ Styles]
        Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
        Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
        [Events]
        Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"""
        self.predialogue = 'Dialogue: 0,'
        self.postdialogue = ',Default,,0,0,0,,'

    def srt(self):
        self.debug()
        if self.argc < 3: self.usage(self.args[1])
        if self.argc >= 3: sourcefile = self.args[2]
        content = []
        with open(sourcefile,'rb') as fh:
            self.fsource = fh.read()
        self.fsource = self.fsource.replace(b'\r',b'').decode(\
        self.codec(infile=sourcefile)).strip('\n').split('\n')
        index = 0
        for i in self.fsource:
            if not re.match('^Dialogue:.*',i):continue
            content = i.split(',')
            index = index + 1
            print(index)
            print(''.join('0' + content[1] + '0' + ' --> '+ '0' + content[2] + '0'))
            print(''.join(content[9:]))
            print()
     
    def ass(self):
        self.debug()
        if self.argc < 3: self.usage(self.args[1])
        if self.argc >= 3: sourcefile = self.args[2]
        content = []
        with open(sourcefile,'rb') as fh:
            self.fsource = fh.read()
        self.fsource = self.fsource.replace(b'\r',b'').decode(\
        self.codec(infile=sourcefile)).strip('\n').split('\n\n')
        print(self.scriptinfo.replace('    ',''))
        for i in self.fsource:
            i = i.replace('-->','\n')
            content = i.split('\n')
            if len(content) < 4: continue
            print(self.predialogue + \
            content[1].replace(',','.').strip(' ').removeprefix('0').removesuffix('0') \
            + ',' + \
            content[2].replace(',','.').strip(' ').removeprefix('0').removesuffix('0') + \
            self.postdialogue + ''.join(content[3:len(content)]))

    def codec(self,infile='misc/source'):
        self.debug()
        infile = os.path.realpath(infile)
        proc = self.run(cmd='file -b ' + infile,stdout=subprocess.PIPE)
        if proc == None:return 
        if proc.stdout.split()[0] not in self.allcodec: return proc.stdout.split()[0]
        return self.allcodec[proc.stdout.split()[0]]

    def timeshift(self):
        self.debug()
        if self.argc < 4: self.usage(self.args[1])
        if self.argc >= 3: sourcefile = self.args[2]
        if self.argc >= 4: shift = self.args[3]
        self.content = []
        with open(sourcefile,'rb') as fh:
            self.fsource = fh.read()
        self.fsource = self.fsource.replace(b'\r',b'').decode(\
        self.codec(infile=sourcefile)).strip('\n').split('\n\n')
        for i in self.fsource:
            i = i.strip('\n')
            length = len(i.split('\n'))
            if length < 3:
                print('missing content: ' + sourcefile + ':'\
                + i,file=sys.stderr)
                return 1
            data = i.split('\n',2)
            self.content.append( data[0] + self.fsep \
            + self.timing(time=data[1],shift=shift) + self.fsep \
            + data[2].replace('\n',' ').strip('\n'))
        print('\n\n'.join(self.content))

    def timing(self,time='20:01:00,370 --> 22:01:04,234',shift='01:01:04,234,-'):
        self.debug()
        self.res = []
        self.shift = re.split('[:,.]',shift)
        self.time = time.split('-->')
        self.time = [ re.split('[:,]',self.time[0]), re.split('[:,]',self.time[1]) ]
        self.op = self.shift[4]
        self.shift = int(self.shift[3]) + int(self.shift[2]) * 1000 + \
        int(self.shift[1]) * 60000 + int(self.shift[0]) * 3600000

        for i in range(len(self.time)):
            self.res.append(int(self.time[i][3]) + int(self.time[i][2]) * 1000 + \
            int(self.time[i][1]) * 60000 + int(self.time[i][0]) * 3600000)
            self.res[i] = self.operator[self.op](self.res[i],self.shift)
            self.time[i][0] = (self.res[i] // 3600000)
            self.time[i][1] = (self.res[i] - self.time[i][0] * 3600000) // 60000
            self.time[i][2] = (self.res[i] - self.time[i][0] * 3600000\
            - self.time[i][1] * 60000) // 1000 
            self.time[i][3] = (self.res[i] - self.time[i][0] * 3600000\
            - self.time[i][1] * 60000 - self.time[i][2] * 1000)
            self.res[i] = ''
            delimiter = ':'
            width = 2
            for j in range(len(self.time[i])):
                if j == 3:
                    delimiter = ','
                    width = 3
                res = str(self.time[i][j]).rjust(width,'0')
                self.res[i] += delimiter + res

            self.res[i] = self.res[i].strip(':')
        return ' --> '.join(self.res)

    def pretranslate(self):
        self.debug()
        if self.argc < 4: self.usage(self.args[1])
        if self.argc >= 3: sourcefile = self.args[2]
        if self.argc >= 4: dicfile = self.args[3]
        self.dic = {}
        self.content = []
        with open(sourcefile,'rb') as fh:
            self.fsource = fh.read()
        self.fsource = self.fsource.replace(b'\r',b'').decode(\
        self.codec(infile=sourcefile)).strip('\n').split('\n\n')
        for i in self.fsource:
            i = i.strip('\n')
            length = len(i.split('\n'))
            if length < 3:
                print('missing content: ' + sourcefile + ':'\
                + i,file=sys.stderr)
                return 1
            data = i.split('\n',2)
            self.content.append( '{' + data[0] + '} '\
            + data[2].replace('\n',' ').strip('\n'))
        with open(dicfile,'rb') as fh:
            self.fdic = fh.read()
        self.fdic = self.fdic.replace(b'\r',b'').decode(\
        self.codec(infile=dicfile)).strip('\n').split('\n')
        for i in self.fdic:
            if re.match('^#',i):continue
            self.dic[i.split(':')[1]] = str(self.dicindex)
            self.dicindex += 1

        linenumber = 0
        for i in range(len(self.content)):
            self.content[i] = re.sub('\w+|\.\.\.',self.lookup,self.content[i])
            print(self.content[i],end='\n')

    def lookup(self,match):
        i = match.group(0)
        if i in self.dic:
             if self.dic[i].isascii(): return ' ' + self.dic[i] + ' '
             else: return self.dic[i] 
        else: return i

    def posttranslate(self):
        self.debug()
        if self.argc < 5: self.usage(self.args[1])
        if self.argc >= 3: sourcefile = self.args[2]
        if self.argc >= 4: dicfile = self.args[3]
        if self.argc >= 5: targetfile = self.args[4]
        self.dic = {}
        self.content = []
        with open(sourcefile,'rb') as fh:
            self.fsource = fh.read()
        self.fsource = self.fsource.replace(b'\r',b'').decode(\
        self.codec(infile=sourcefile)).strip('\n').split('\n\n')
        for i in self.fsource:
            length = len(i.split('\n'))
            if length < 3:
                print('missing content: ' + sourcefile + ':'\
                + i,file=sys.stderr)
                return 1
            data = i.split('\n',2)
            self.content.append( data[0] + self.fsep + data[1])
        with open(dicfile,'rb') as fh:
            self.fdic = fh.read()
        self.fdic = self.fdic.replace(b'\r',b'').decode(\
        self.codec(infile=dicfile)).strip('\n').split('\n')
        for i in self.fdic:
            if re.match('^#',i):continue
            self.dic[str(self.dicindex)] = i.split(':')[2]
            self.dicindex += 1
        with open(targetfile,'rb') as fh:
            self.ftarget = fh.read()
        self.ftarget = self.ftarget.replace(b'\r',b'').decode(\
        self.codec(infile=dicfile)).strip('\n').replace('}','} ').split('\n')
        if len(self.content) != len(self.ftarget):
            self.debug(info='diff length in:' + sourcefile +\
            ':' + str(len(self.fsource)) + ' ' + targetfile +\
            ':' + str(len(self.ftarget)))
            return 1
        for i in range(len(self.content)):
            self.data = re.sub('{.*} *','',self.ftarget[i],1)
            self.content[i] = self.fsep.join(self.content[i].split(self.fsep)[:2])
            self.content[i] += self.fsep + re.sub('654\d\d\d',self.lookup,self.data)
        for i in self.content:
            for j in i.split(self.fsep):
                print(j)
            print()

    def pposttranslate(self):
        self.debug()
        if self.argc < 5: self.usage(self.args[1])
        if self.argc >= 3: sourcefile = self.args[2]
        if self.argc >= 4: dicfile = self.args[3]
        if self.argc >= 5: targetfile = self.args[4]
        self.dic = {}
        self.content = []
        with open(sourcefile,'rb') as fh:
            self.fsource = fh.read()
        self.fsource = self.fsource.replace(b'\r',b'').decode(\
        self.codec(infile=sourcefile)).strip('\n').split('\n\n')
        for i in self.fsource:
            length = len(i.split('\n'))
            if length < 3:
                print('missing content: ' + sourcefile + ':'\
                + i,file=sys.stderr)
                return 1
            data = i.split('\n',2)
            self.content.append( data[0] + self.fsep + data[1])
        with open(dicfile,'rb') as fh:
            self.fdic = fh.read()
        self.fdic = self.fdic.replace(b'\r',b'').decode(\
        self.codec(infile=dicfile)).strip('\n').split('\n')
        for i in self.fdic:
            if re.match('^#',i):continue
            self.dic[str(self.dicindex)] = i.split(':')[2]
            self.dicindex += 1
        with open(targetfile,'rb') as fh:
            self.ftarget = fh.read()
        self.ftarget = self.ftarget.replace(b'\r',b'').decode(\
        self.codec(infile=dicfile)).strip('\n').split('\n')
 
        if len(self.content) != len(self.ftarget):
            self.debug(info='diff length in:' + sourcefile +\
            ':' + str(len(self.fsource)) + ' ' + targetfile +\
            ':' + str(len(self.ftarget)))
            return 1
        # Differs on output language.
        delimiter = ''
        for i in range(len(self.content)):
            self.data = delimiter.join(self.ftarget[i].split()[1:])
            self.content[i] = self.fsep.join(self.content[i].split(self.fsep)[:2])
            self.content[i] += self.fsep + re.sub('654\d\d\d',self.lookup,self.data)
        for i in self.content:
            for j in i.split(self.fsep):
                print(j)
            print()

    def usage(self,option=1):
        if option in self.message:
            print(self.message[option].replace("@","\n    "))
        else:
            for key in self.message:
                print(key,self.message[key].replace("@","\n    "))
        exit(1)

    def run(self, cmd='',infile='',outfile='',stdin=None,stdout=None,
        text=True,pass_fds=[],exit_errorcode='',shell=False):
        try:
            proc = None
            emit = __file__ + ':' + sys._getframe(1).f_code.co_name + ':' \
            + str(sys._getframe(1).f_lineno)
            if infile != '': stdin = open(infile,'r')
            if outfile != '': stdout = open(outfile,'w')
            proc = subprocess.run(cmd.split(),
            stdin=stdin,stdout=stdout,text=text,check=True,
            pass_fds=pass_fds,shell=shell)
            if infile != '': stdin.close() 
            if outfile != '': stdout.close()
            if not isinstance(proc,subprocess.CompletedProcess):
                self.debug(info='end 1',emit=emit)
                return None
            if isinstance(proc.stdout,str):
                proc.stdout = proc.stdout.rstrip('\n')
                self.debug(info='end 2',emit=emit)
                return proc
        except subprocess.CalledProcessError as e:
            emit += ':' + str(e.returncode)
            if exit_errorcode == '':
                if e.returncode != 0:
                    self.debug(info='end 3: ',emit=emit)
                    exit()
            elif e.returncode == exit_errorcode:
                self.debug(info='end 4',emit=emit)
                exit()
            return None

    def debug(self,info='',outfile='',emit=''):
        if not self.debugging: return
        emit = sys._getframe(1).f_code.co_name + ':' \
        + str(sys._getframe(1).f_lineno) + ':' + info + ':' + emit
        print(emit,file=sys.stderr)


if __name__ == '__main__':
    diasub = Diasub(sys.argv)
    if diasub.args[1] not in diasub.option: diasub.usage()
    try:
        diasub.option[diasub.args[1]]()
    except KeyboardInterrupt:
        diasub.debug(info='user ctrl-C')
    finally:
        diasub.debug(info='session finally end')
        for key,value in diasub.__dict__.items():
            if isinstance(value,io.TextIOWrapper):
                value.close()
                continue
            if isinstance(value,tempfile._TemporaryFileWrapper):
                value.close() 
                if os.access(value.name,os.R_OK): os.unlink(value.name)

        with open('/tmp/diasublog','w') as diasub.logfh:
            print(diasub.__dict__,file=diasub.logfh)
