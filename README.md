# bruteforce-md5
A distributed engine/dispatcher system for brute-forcing MD5 hashes. Using lexicographical brute-forcing.

`main.py` - The server manages connections, dispatches hash-cracking tasks to engine clients, and relays results to requesting clients.

`engine.py` - The engine client responsible for brute-forcing MD5 hashes. It can be deployed on any machine and processes assigned password ranges in parallel.

`client.py` - The user prompt requests the server to brute-force a specific MD5 hash and receive the result once found.

This project was assigned to me during high school as part of a mission to create a small project that performs "brute-forcing".

![image](https://github.com/user-attachments/assets/7d13d241-a3c5-401c-a698-1dcd11210b4c)
