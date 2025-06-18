FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 步骤 1: 切换到国内镜像源以加速
# 使用更稳健的方法：直接重写整个apt源配置文件，指向清华大学TUNA镜像源
RUN { \
    echo "Types: deb"; \
    echo "URIs: https://mirrors.tuna.tsinghua.edu.cn/debian/"; \
    echo "Suites: bookworm bookworm-updates"; \
    echo "Components: main contrib non-free non-free-firmware"; \
    echo "Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg"; \
    echo ""; \
    echo "Types: deb"; \
    echo "URIs: https://mirrors.tuna.tsinghua.edu.cn/debian-security/"; \
    echo "Suites: bookworm-security"; \
    echo "Components: main contrib non-free non-free-firmware"; \
    echo "Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg"; \
    } > /etc/apt/sources.list.d/debian.sources

# 步骤 2: 安装系统依赖
# 更新软件源列表并安装编译Python包所需的系统工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    gcc \
    libc6-dev \
    libffi-dev \
    libssl-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 步骤 3: 安装Python依赖
# 先只复制 pyproject.toml 和 README.md，这样可以利用Docker层缓存
# 只要这些文件不变，依赖就不会重新安装
COPY pyproject.toml README.md ./

# 利用BuildKit缓存并指定清华大学TUNA镜像源来加速uv的安装过程
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system \
    --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    .

# 步骤 4: 复制应用源代码
# 在依赖安装完成后再复制项目代码
COPY . .

EXPOSE 8000

# 运行应用
CMD ["uv", "run", "python", "server.py", "--host", "0.0.0.0", "--port", "8000"]
