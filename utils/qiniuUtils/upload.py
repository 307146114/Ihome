# -*- coding: utf-8 -*-
# flake8: noqa

from utils.qiniuUtils.qiniu import Auth, put_file, etag, urlsafe_base64_encode, put_data
import utils.qiniuUtils.qiniu.config
from utils.qiniuUtils.qiniu.compat import is_py2, is_py3

# 需要填写你的 Access Key 和 Secret Key
access_key = 'XkwjtYAh-Wjd08uB8yX8S3Sm3fEb_Tu-Nd_NjFlS'
secret_key = 'WzOoSdgxH4J5SgVYZF2B4zXzBkAEf2zUE1U1j4X0'

def upload(imge_bytes):
    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'ihome20200529'

    # 上传到七牛后保存的文件名
    # key = 'my-python-七牛.png'

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    # 要上传文件的本地路径
    # localfile = '/Users/jemy/Documents/qiniu.png'

    ret, info = put_data(token, None, imge_bytes)
    # print(ret)
    # print(info)
    return  ret['key']
    #
    # if is_py2:
    #     assert ret['key'].encode('utf-8') == key
    # elif is_py3:
    #     assert ret['key'] == key
    #
    # assert ret['hash'] == etag(localfile)

if __name__ == '__main__':
    file_name = input('请输入要上传的文件:')
    imge_file = open(file_name, 'rb')
    upload(imge_file.read())
    imge_file.close()
