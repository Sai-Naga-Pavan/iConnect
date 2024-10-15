# iConnect

iConnect is a social media application that allows users to follow each other, upload posts, and engage with others by liking and commenting on their content. Additionally, users can chat with one another for enhanced interaction.

## Features

- **User Registration and Authentication**: Secure user sign-up and login process.
- **Follow and Unfollow Functionality**: Users can follow and unfollow each other.
- **Post Management**: Users can upload posts and share them with others.
- **Likes and Comments**: Users can like and comment on posts shared by others.
- **Real-time Chat**: Users can chat with each other in real time.
- **Notifications**: Users receive notifications for relevant actions, such as new likes, comments, and follow requests.

## Technologies

- Python 3.x
- FastAPI
- Motor (async MongoDB driver)
- JWT for authentication
- WebSockets for real-time notifications
- MongoDB

## Setup

### Prerequisites

Make sure you have the following installed:

- Python 3.x
- pip (Python package manager)
- MongoDB

### Cloning the Repository

Clone the repository to your local machine:
git clone <repo-url>
cd iConnect

### Create a virtual environment
python -m venv venv

### Activate the virtual environment
#### On Windows
venv\Scripts\activate
#### On macOS/Linux
source venv/bin/activate

###Install Dependencies
pip install -r requirements.txt

###Environment Variables
MONGO_URL=<YOUR_URL>
DATABASE_NAME=<DB_NAME>
JWT_SECRET_KEY=<KEY>

###Run the Application
python main.py

Visit http://localhost:8000/docs in your browser to access the Swagger UI and explore the API endpoints.
