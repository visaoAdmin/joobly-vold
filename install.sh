#!/bin/bash
sudo apt install redis-server && 
sudo systemctl start redis && 
sudo systemctl start redis && 
wget http://download.redis.io/redis-stable.tar.gz -P ~/ &&
tar xvf ~/redis-stable.tar.gz -C ~/ &&
cd ~/redis-stable/ &&
make -j$(nproc) &&
sudo make install &&
pip3 install rq