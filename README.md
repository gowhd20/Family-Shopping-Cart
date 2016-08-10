# Initiative
To create mobisocial context-aware application that supports future family life.

# Motivation
We have designed the application with an aim of resolving common family issues.
Managing family supplies has been done in an analogue manner, such as making a phone call
to the husband/wife or even children who sat in better convenience position to bring the items needed,
or texting which might be confused later with any general conversation. 

# System
- Android mobile client application

- Restful web server situated on google cloud platform
	
# Features
- User is able to add items needed to the family shared shopping-cart with nominated family members
	who would receive the notifications as the item added.
	
- System send notifications to the listed members.

- User who receives the notification can declair that he/she would purchase the registered item.
	Also this action is open to all other members who didn't receive the notification as well.
	
- User who requested itmes can delete the item from the shared list as needed.

- Server collects weather information according to the timestamp that registered along with 
	items. In future this would provide recommendation of key words of items that were most requested
	throughout the season or the specific time by leveraging key word based learning algorithm implemented
	in the server.

# Work-in-progress
- Taking photo of the item

- Improve user experience in adding family members

- family comments 
	
# Tools
	- Java, Python

# Bug-fix Report
- 08/08/2016
1. 12:05, in model_mongodb.py, GCM requests are disabled while server updates, and will stay until needed later 
2. 12:37, in requests_item.py, reqparse type for 'optional_data' was modified from 'dict' to 'list'
3. 12:40, in requests_item.py 'RequestsIndex', indicated data info of sender was modified from 'google_token' to 'uid'	

- 09/08/2016
1. 13:17, in model_mongodb.py, writing image files implemented also in relation, 
new database referring code "mongo_meta.py" was added
2. 13:17, in model_mongodb.py, some public functions are moved to api.py
3. 18:10, completed testing on image writing, adding, and updating

- 10/08/2016
1. 13:43, in model_mongodb.py, requests_item.py, delete image has implemented and tested 
2. 19:00, get images by request implemented and the test has completed, applied to the server 
3. 20:00, rest format and api were modified

# Video Demo
https://youtu.be/5HEmZdVGkuE
	
# System screenshot
![alt tag](https://raw.github.com/gowhd20/Family-Shopping-Cart/master/images/Screenshot_2016-05-01-18-18-47.png)

![alt tag](https://raw.github.com/gowhd20/Family-Shopping-Cart/master/images/Screenshot_2016-05-01-18-17-43.png)

![alt tag](https://raw.github.com/gowhd20/Family-Shopping-Cart/master/images/Screenshot_2016-05-01-18-17-08.png)

![alt tag](https://raw.github.com/gowhd20/Family-Shopping-Cart/master/images/Screenshot_2016-05-01-18-14-50.png)

![alt tag](https://raw.github.com/gowhd20/Family-Shopping-Cart/master/images/Screenshot_2016-05-01-18-14-25.png)

![alt tag](https://raw.github.com/gowhd20/Family-Shopping-Cart/master/images/Screenshot_2016-05-01-18-13-32.png)

![alt tag](https://raw.github.com/gowhd20/Family-Shopping-Cart/master/images/13115363_1129551520423609_153421984_n.png)


	
	
	
