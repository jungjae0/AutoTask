#### 로컬에서 서버로 파일 전송

파일 하나 전송
```angular2html
scp local_file_path username@server_ip:/home/username/remote_folder/
```
파일 여러개 전송
```angular2html
scp local_file_path1 local_file_path2 username@server_ip:/home/username/remote_folder/
```
폴더 전송
```angular2html
scp -r local_folder username@server_ip:/home/username/remote_folder/
```

#### AWS
AWS 서버 접속

```angular2html
ssh -i ~/server/pem_key_file_name.pem username@server_ip
```


AWS 서버 파일 전송
```angular2html
scp -i~/server/pem_key_file_name.pem locale_file_path ec2-user@server_ip:/home/username/remote_folder
```