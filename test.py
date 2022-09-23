import email.header
print(email.header.decode_header('=?utf-8?Q?Subject=c3=a4?=X=?utf-8?Q?=c3=bc?=')[0])