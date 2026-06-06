# Online Auction and Bidding System
## Overview
This repository contains the final project for CS166 at the University of California, Riverside. This project tracks the users, bids, payments, auctions, shipments, and items.

## ER Diagram
<img width="1290" height="993" alt="675972164_2359427107858395_8328466265269416460_n" src="https://github.com/user-attachments/assets/4169ed95-3cd9-4f3c-8f67-e62a6aad1e86" />

## Files
'startPostgreSQL.sh': Initializes PostgreSQL environment
'createPostgreDB.sh': Creates a new database and initializes it with 'cs166_phase2_schema.sql'
'stopPostgreSQL.sh': shuts down the PostgreSQL environment
'cs166_phase2_schema.sql': Creates tables for entities 'users', 'item', 'auction', 'bid', 'payment', 'shipment'
'indexes.sql': Allocates index pointers on foreign keys 
'app.py': Python application for command-line program

## How to run
1. run startPostgreSQL.sh
2. run createPostgreDB.sh
3. apply indexes using 'cs166_psql akim461_Project_DB < indexes.sql'
4. run app.py using 'python3 app.py'
5. when finished, shut down the server using stopPostgreDB.sh

## Members
Anne Kim, akim461
Hayley Wong, hwong070
