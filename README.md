

This is a simple POC that shows how to use the [Amazon Lex](https://aws.amazon.com/lex/) API to programmatically generate bots based on a configuration file. This code simply
illustrates how to use use the APIs and is definitely not production-ready code.

In order to run this sample code, you need [boto3](https://github.com/boto/boto3) installed:

```
sudo pip install boto3 --upgrade
```

Credentials need to be in ~/.aws/config / ~/.aws/credentials or the instance needs an attached IAM role that permits it to read/write to Lex.

Once you have your credentials/role in place and boto3 installed, run:

```
python generate.py
```

