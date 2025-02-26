### XFO-depth Fuzzer 

* Fuzz browser behavior with cross-origin grandparent -> same-origin children frames.

### Usage 

1. Setup `/etc/hosts` like the following:
```
127.0.0.1 attacker.com
127.0.0.1 victim.com
```

2. Run the fuzzer (`-d` for desired depth):

```bash
./fuzz.sh -d 200
```

3. Open the [https://attacker.com:1337/grandparent.html](https://attacker.com:1337/grandparent.html) in your browser. 

