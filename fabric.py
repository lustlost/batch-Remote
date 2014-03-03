#!/usr/bin/python
import os,sys,time,string,random,copy
from fabric.api import *
from fabric.colors import *
import socket
from fabric.exceptions import NetworkError

pass_len=16
bf=1000
t = time.strftime('%Y%m%d-%H%M%S',time.localtime(time.time()))
logdir='logs/'+t

def mkdir(path):
    path=path.strip()
    isExists=os.path.exists(path)
    if not isExists:
        print 'log is in '+path
        os.makedirs(path)
        return True
    else:
        print path+'logdir is exist'
        return False

mkdir(logdir)

def log(logdir,results,type='1',name=None):
    if type=='1':
        logfile=open(logdir+'/'+env.host,'a')
        logfile.write(results)
        logfile.close()
    else:
        logfile=open(logdir+'/'+name,'a')
        logfile.write(results)
        logfile.close()

def GenPassword(length=pass_len):
   chars=string.ascii_letters+string.digits
   return ''.join([random.choice(chars) for i in range(length)])

@task
def info(arg1,arg2=None):
    hosts_file=arg1
    cmd_file=arg2
    global command

    for line in open(hosts_file,'r'):
        line_host = 'root@%s:%s'%(line.split()[0],line.split()[1])
        env.hosts.append(line_host)
        env.passwords[line_host]=line.split()[2]
    if arg2:
        command=open(cmd_file,'r').read()
	
@task
@parallel(pool_size=bf)
def go():
    try:
        results=run(command,quiet=True)
        results+='\n'
        log(logdir,results)
        print (green('\n'+'='*10+'This is '+env.host+' Results....'+'='*10+'\n'))
        print results
        print (yellow('log in '+logdir+'/'+env.host))
    except NetworkError:
        results=env.host+' is down or port wrong...\n'
        log(logdir,results,type=2,name='error')
        print (green('\n'+'='*10+'This is '+env.host+' Results....'+'='*10+'\n'))
        print results
        print (red('log in '+logdir+'/error'))
    except:
        results=env.host+' password is wrong \n'
        log(logdir,results,type=2,name='error')
        print (green('\n'+'='*10+'This is '+env.host+' Results....'+'='*10+'\n'))
        print results
        print (red('log in '+logdir+'/error'))

@task
def czc():
    with hide('running'):
        run('''ID=`dmidecode | grep N14 | tail -1 | awk -F':' '{print $2}' `;IP=`ifconfig eth0 | grep  "inet addr:" | awk -F: '{print $2}' | awk '{print $1}'`;echo "$IP:$ID"''')

@task
@parallel(pool_size=bf)
def upload(local_path,remote_path):
    try:
        put(local_path, remote_path, use_sudo=False, mirror_local_mode=False, mode=None)
    except NetworkError:
        results=env.host+' is down or port wrong...'
        log(logdir,results,type=2,name='error')
        print (red('log in '+logdir+'/error'))
    except:
        results=env.host+' password is wrong'
        log(logdir,results,type=2,name='error')
        print (red('log in '+logdir+'/error'))
    finally:
        print (green('\n'+'='*10+env.host+' upload ok'+'='*10+'\n'))

@task
@parallel(pool_size=bf)
def download(remote_path, local_path=None):
    try:
        get(remote_path, local_path)
    except NetworkError:
        results=env.host+' is down or port wrong...'
        log(logdir,results,type=2,name='error')
        print (red('log in '+logdir+'/error'))
    except:
        results=env.host+' password is wrong'
        log(logdir,results,type=2,name='error')
        print (red('log in '+logdir+'/error'))
    finally:
        print (green('\n'+'='*10+env.host+' download ok'+'='*10+'\n'))

@task
def passwd():
    password=GenPassword()
    try:
        run('echo %s | passwd root --stdin;history -c' % password)
        newpass_info='%s\t%s\n'%(env.host,password)
    except NetworkError:
        results=env.host+' is down or port wrong...'
        log(logdir,results,type=2,name='error')
    except:
        results=env.host+' password is wrong'
        log(logdir,results,type=2,name='error')
    finally:
        log(logdir,newpass_info,type=2,name='error')
