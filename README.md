# Designing Assistant for Data-Driven Stories

### Description
The foundation of this project lies in understanding the needs and challenges faced by analysts and writers in today’s data-driven writing process. In a world where people rely heavily on data, we noticed that analysts and writers often encounter problems when it comes to working with this data, although with their backgrounds, they excel in creating compelling narratives and stories. Our project, aims to make the data-driven writing process easier and faster by offering a comprehensive writing tool that essentially analyzes the data for the user, empowering writers to leverage data effectively while focusing on their strengths that lie in storytelling.

## Installation

### Getting started

Clone the repository into your local machine. The src folder contains all of the code, so this is the only essential folder for starting the program.

### Setting up FRONT END

- Node v20.9.0 and npm version 10.1.0 are required for this application. To check your current versions, execute these commands:

```
node --version
npm --version
```

- In the folder `src/frontend/front-end`, create a file `.env` with the following contents:

```
NEXTAUTH_SECRET=vVTTYRya+N969dBKFCOdsjnxrFC3Owe4I0AaT3W8iPcnw9+JXlng01QNQ+j2FOrJ
RoD47b9TcWwNiw40RgxwzdG/V3uEBfJB4ylLgruYhOcoF6HZo/UEAvDO0nyGjYRB
lZZYgMlgiiZi0sTKr23mt9MEmduWmRtjwuo+R9upWWJz5PqP2EScghlR9tPwwhlp
rgnJk+iVD2hIGAGD6dccp7sDBjy4hC16kJQX/8JG4WNS7nq17H0sHJNRHWKfdmwQ
ijNi3P2bJ1M=
NEXTAUTH_URL=http://localhost:3000
NEXT_PUBLIC_LOCAL_URL=http://127.0.0.1:8080
MONGODB_URI=mongodb+srv://lostm:RlT5ix66d7jcajHr@cluster0.26a1r0n.mongodb.net/d
```

- In the folder `src/frontend/front-end`, execute the following two commands:

```
npm install
npm run dev
```

### Setting up BACK END

- Create a virtual environment: 

`python -m venv /path/to/new/virtual/environment`

- To activate this environment, use the following command `<venv>\Scripts\activate`. This command is for Windows, it may differ depending on the system that is used.

- In the folder `src/backend`, create a file `.env` with the following contents:

```
MONGO_URI=mongodb+srv://lostm:RlT5ix66d7jcajHr@cluster0.26a1r0n.mongodb.net/?retryWrites=true&w=majority
SECRET_KEY=5957450d7a3e437980bc3566be2baf65
```

- In the folder `src/backend`, execute the following two commands:

```
pip install -r requirements.txt
python run.py
```


## Authors and acknowledgment
- Sarib Kashif
- Leo Srayeddin
- Omar Zahir
- Talha Amjad
- Mahad Aziz
- Supervisor: Professor Swati Mishra
