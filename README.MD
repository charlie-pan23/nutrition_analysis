### 称ip
#### 开放端口 
```
172.20.10.11
```

### 电脑ip
#### 开放端口 5000
```
172.20.10.3
```


sudo iptables -A INPUT -p tcp --dport 5173 -j ACCEPT
