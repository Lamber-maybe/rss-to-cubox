# RSS to Cubox

这是一个Python脚本，用于从多个RSS源获取文章，并发送到Cubox。该脚本支持自定义RSS配置和黑名单作者列表。

## 功能

- 加载RSS源配置
- 加载黑名单作者列表
- 获取RSS源的文章
- 过滤掉黑名单作者的文章
- 通过Cubox API发送新文章的通知
- 使用SQLite数据库存储已处理的文章标识符

## 安装

1. 克隆此仓库：

   ```bash
   git clone https://github.com/Lamber-maybe/rss-to-cubox.git 
   cd rss-to-cubox
   ```

2. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

## 使用

运行脚本时需要提供Webhook URL：

新建 `webhook_config.txt` 将消息通知用的webhook放在该文件中，然后运行脚本

```
python main.py
```


## 配置

- **RSS_GITHUB_URL**: 包含RSS源配置的GitHub文件URL。
- **GITHUB_BLACKLIST_URL**: 包含黑名单作者的GitHub文件URL。
- **DB_FILE**: SQLite数据库文件名，默认是`rss_entries.db`。

## 贡献

欢迎贡献！请 fork 此仓库并提交 pull request。

## 许可证

此项目使用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。
