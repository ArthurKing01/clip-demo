## clip

## 环境搭建

python版本：3.9.x

### 安装ffmpeg
`brew install ffmpeg`

### 创建虚拟环境
`python3.9 -m venv venv`

### 切换至虚拟环境
`source venv/bin/activate`

### 设置pip镜像源
`pip install -U pip`
`pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple`

### 安装依赖
`pip install -r requirements.txt`

### 安装CLIP
`pip install git+https://github.com/openai/CLIP.git`


### 开始

`python main.py`