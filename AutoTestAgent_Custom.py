#
!
/
usr
/
bin
/
env

python3
# 
-
*
-

coding
:

utf
-
8

-
*
-
# 
定
制
化
指
令
:

每
次
都
選
拉
斯
維
加
斯
# 
適
用
狀
態
:

SelectScene

(
賽
道
選
擇
流
程
)
# 
操
作
邏
輯
:

在
賽
道
選
擇
時
固
定
選
擇
拉
斯
維
加
斯

import

sys
import

os
import

socket
import

time
import

random
import

signal
import

threading
from

datetime

import

datetime

# 
確
保
正
確
的
工
作
目
錄
和
路
徑
script
_
dir

=

os.path.dirname
(
os.path.abspath
(
_
_
file
_
_
)
)
os.chdir
(
script
_
dir
)
sys.path.insert
(
0,

script
_
dir
)

try
:




from

ProtoSchema.GameFlowData
_
pb2

import

GameFlowData




from

ProtoSchema.InputCommand
_
pb2

import

InputCommand,

EInputKeyType




print
(
"
✅

Protobuf

模
組
載
入
成
功
"
)
except

ImportError

as

e
:




print
(
f"
❌

無
法
導
入

Protobuf

模
組
:

{
e
}
"
)




input
(
"
按

Enter

鍵
結
束
..."
)




sys.exit
(
1
)

class

AutoTestAgent
:




def 
init
(
self
)
:








self.host

=

"127.0.0.1"








self.port

=

8587








self.socket

=

None








self.running

=

False








self.connected

=

False








self.log
_
file

=

None









#

按
鍵
映
射

-

使
用
實
際
的

EInputKeyType

枚
舉








self.key
_
mapping

=

{












"UP"
:

EInputKeyType.INPUT
_
KEY
_
UP,












"DOWN"
:

EInputKeyType.INPUT
_
KEY
_
DOWN,












"LEFT"
:

EInputKeyType.INPUT
_
KEY
_
LEFT,












"RIGHT"
:

EInputKeyType.INPUT
_
KEY
_
RIGHT,












"START"
:

EInputKeyType.INPUT
_
KEY
_
START,












"NITRO"
:

EInputKeyType.INPUT
_
KEY
_
NITRO,












"TEST"
:

EInputKeyType.INPUT
_
KEY
_
TEST,












"SERVICE"
:

EInputKeyType.INPUT
_
KEY
_
SERVICE,








}









self.available
_
keys

=

[
"UP",

"DOWN",

"LEFT",

"RIGHT",

"START"
]









#

初
始
化
日
誌








self.init
_
log
(
)









#

設
置
信
號
處
理








signal.signal
(
signal.SIGINT,

self.signal
_
handler
)





def

init
_
log
(
self
)
:








try
:












self.log
_
file

=

open
(
"AutoTestAgent
_
Custom.log",

"w",

encoding
=
"utf
-
8"
)












self.log
(
"
🚀

AutoTestAgent

啟
動
"
)












self.log
(
"
🎯

定
制
化
指
令
:

每
次
都
選
拉
斯
維
加
斯
"
)








except

Exception

as

e
:












print
(
f"
❌

無
法
創
建
日
誌
文
件
:

{
e
}
"
)





def

log
(
self,

message
)
:








timestamp

=

datetime.now
(
)
.strftime
(
"
%
Y
-
%
m
-
%
d

%
H
:
%
M
:
%
S"
)








log
_
message

=

f"
[
{
timestamp
}
]

{
message
}
"









#

輸
出
到
控
制
台








print
(
log
_
message
)









#

輸
出
到
文
件








if

self.log
_
file
:












self.log
_
file.write
(
log
_
message

+

"
\
n"
)












self.log
_
file.flush
(
)





def

signal
_
handler
(
self,

signum,

frame
)
:








self.log
(
"
程
式
已
停
止
"
)








self.running

=

False








if

self.log
_
file
:












self.log
_
file.close
(
)








sys.exit
(
0
)





def

create
_
socket
(
self
)
:








try
:












if

self.socket
:
















self.socket.close
(
)












self.socket

=

socket.socket
(
socket.AF
_
INET,

socket.SOCK
_
DGRAM
)












self.socket.settimeout
(
5.0
)












return

True








except

Exception

as

e
:












self.log
(
f"
❌

創
建

Socket

失
敗
:

{
e
}
"
)












return

False





def

register
_
role
(
self
)
:








try
:












#

發
送
角
色
註
冊












self.socket.sendto
(
b"role
:
agent",

(
self.host,

self.port
)
)













#

等
待
確
認












data,

addr

=

self.socket.recvfrom
(
1024
)












if

data.decode
(
)

=
=

"ok
:
agent"
:
















self.log
(
"
✅

角
色
註
冊
成
功
"
)
















return

True












else
:
















self.log
(
f"
❌

角
色
註
冊
失
敗
，
收
到
:

{
data.decode
(
)
}
"
)
















return

False








except

Exception

as

e
:












self.log
(
f"
❌

角
色
註
冊
異
常
:

{
e
}
"
)












return

False





def

connect
_
to
_
game
(
self
)
:








while

self.running
:












self.log
(
"
🔄

等
待
遊
戲
連
線
..."
)












if

self.create
_
socket
(
)

and

self.register
_
role
(
)
:
















self.connected

=

True
















self.log
(
"
✅

遊
戲
連
線
成
功
，
開
始
接
收
數
據
"
)
















return

True












else
:
















self.log
(
"
❌

遊
戲
連
線
失
敗
，
5
秒
後
重
試
..."
)
















time.sleep
(
5
)








return

False





def

process
_
game
_
data
(
self,

data
)
:








try
:












game
_
data

=

GameFlowData
(
)












game
_
data.ParseFromString
(
data
)













#

記
錄
接
收
的
遊
戲
數
據












self.log
(
f"
📥

接
收
遊
戲
數
據
:
"
)












self.log
(
f"



所
有
欄
位
:

{
game
_
data
}
"
)












self.log
(
f"



狀
態
:

{
game
_
data.current
_
flow
_
state
}
"
)













#

生
成
輸
入












self.send
_
input
(
game
_
data
)













self.log
(
"
=
" 

50
)









except

Exception

as

e
:












self.log
(
f"
❌

處
理
遊
戲
數
據
失
敗
:

{
e
}
"
)





def

send
input
(
self,

game
_
data
)
:








try
:












#

檢
查
是
否
為
賽
道
選
擇
狀
態

(
SelectScene

=

6
)












if

hasattr
(
game
_
data,

'
current
_
flow
_
state
'
)

and

str
(
game
_
data.current
_
flow
_
state
)

=
=

'
6
'
:
















#

在
賽
道
選
擇
狀
態
，
固
定
選
擇
拉
斯
維
加
斯

(
LasVegas

=

1
)
















#

根
據

ETrack

枚
舉
，
拉
斯
維
加
斯
是
第
一
個
選
項
，
使
用

LEFT

導
航
到
正
確
位
置
















selected
_
key

=

"LEFT"
















self.log
(
"
🎯

賽
道
選
擇
狀
態

-

執
行
定
制
化
邏
輯
:

選
擇
拉
斯
維
加
斯
"
)












else
:
















#

其
他
狀
態
使
用
隨
機
輸
入
















selected
_
key

=

random.choice
(
self.available
_
keys
)













#

創
建
輸
入
指
令












input
_
command

=

InputCommand
(
)












input
_
command.key
_
inputs.append
(
self.key
_
mapping
[
selected
_
key
]
)












input
_
command.is
_
key
_
down

=

True












input
_
command.timestamp

=

int
(
time.time
(
) 

1000
)













#

發
送
指
令












self.socket.sendto
(
input
command.SerializeToString
(
)
,

(
self.host,

self.port
)
)













self.log
(
f"
📤

發
送
輸
入
指
令
:

{
selected
_
key
}
"
)









except

Exception

as

e
:












self.log
(
f"
❌

發
送
輸
入
指
令
失
敗
:

{
e
}
"
)





def

listen
_
loop
(
self
)
:








while

self.running

and

self.connected
:












try
:
















data,

addr

=

self.socket.recvfrom
(
4096
)
















self.process
_
game
_
data
(
data
)












except

socket.timeout
:
















continue












except

Exception

as

e
:
















self.log
(
f"
❌

遊
戲
連
線
中
斷
:

{
e
}
"
)
















self.connected

=

False
















break





def

run
(
self
)
:








self.running

=

True








while

self.running
:












if

self.connect
_
to
_
game
(
)
:
















self.listen
_
loop
(
)












if

self.running
:
















self.log
(
"
❌

遊
戲
連
線
中
斷
，
5
秒
後
重
試
..."
)
















time.sleep
(
5
)

def

main
(
)
:




try
:








agent

=

AutoTestAgent
(
)








agent.run
(
)




except

KeyboardInterrupt
:








print
(
"
\
n
程
式
已
停
止
"
)




except

Exception

as

e
:








print
(
f"
❌

程
式
執
行
錯
誤
:

{
e
}
"
)








input
(
"
按

Enter

鍵
結
束
..."
)

if 
name

=
=

"
_
_
main
_
_
"
:




main
(
)