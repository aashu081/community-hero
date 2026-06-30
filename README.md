# Community Hero

A simple app made to help people report problems in their area, made for the hackathon. It lets citizens report civic issues like potholes, broken streetlights, garbage and water leakage, and lets authorities track and fix them using AI help.

## Live Links

Citizen App: https://community-hero-f33cc.web.app/

Authority Dashboard: https://community-hero-f33cc.web.app/dashboard.html

Backend API: https://community-hero-782012687300.asia-south1.run.app

## Problem Statement Selected

Communities often face problems like potholes, water leakages, broken streetlights, garbage piling up, and other public problems. But reporting these problems is hard. People do not know who to call, the reports get lost, there is no tracking, and there is no transparency between the people and the authority. We picked this problem to make reporting and fixing these issues simple and fast with the help of AI.

## Solution Overview

Community Hero is an app where any normal person can report a problem they see around them. The person opens the app, the location is taken automatically using GPS, and the live camera opens so the user can take a photo of the problem right there. The user just adds their name and phone number and sends the complaint. An AI model called an LLM, which means large language model, a smart AI brain that can understand images and text, looks at the photo and decides what the problem is, how serious it is, and which department should fix it. This whole report then goes to an Authority Dashboard where the officials can see all complaints on a live map, check the photo and AI report, go to the exact spot using Google Maps, and update the status as Reported, In Progress or Resolved. This status update is shown back to the citizen too, so they always know what is happening with their complaint.

## Key Features

* Live camera only photo reporting, so the photo and the place are always real and matching. No old photos from gallery are allowed, so people cannot complain later from a different place like their home.
* Automatic GPS location, so the user does not need to know or type the name of the street or area. This also lets an outsider who does not know the area report a problem easily.
* AI powered issue categorization using an LLM, which reads the photo and decides the category like Pothole or Damaged Road, the severity like Low, Medium, High or Critical, the right department, and the urgency of fixing it.
* A live map on the Authority Dashboard showing every complaint as a pin, with filters for Reported, In Progress, Resolved and Critical issues.
* One click to open the exact complaint location in Google Maps for the authority to go and fix it.
* Real time status tracking, so when the authority updates a complaint, the same update shows in the citizens My Complaints page right away.
* Upvote option on complaints so other citizens can support a problem they also face, showing how many people are affected.

## Technologies Used

* HTML, CSS and JavaScript for the citizen app and the authority dashboard.
* Python with FastAPI for the backend server that handles complaints and talks to the AI model.
* Groq LLM API for fast AI powered image understanding and issue categorization. We could not add Gemini API yet because of some errors and issues we faced while building, but it can surely be added later since the system is built to work with any LLM.
* Docker for packaging the backend so it runs the same way everywhere.

## Google Technologies Utilized

* Google Cloud Run to host and run our backend server live.
* Firebase Firestore as our live database to store all the complaints and their status.
* Firebase Hosting to host our citizen app and authority dashboard live on the web.
* Google Maps for showing the live map of complaints and for opening the exact pinpoint location for the authority.

## Project Structure

```
community hero
  backend
    main.py
    requirements.txt
    Dockerfile
  frontend
    index.html
    dashboard.html
```

## How To Run Locally

Backend setup

```
cd backend
pip install -r requirements.txt
```

Add your own .env file inside the backend folder with your Gemini API key/Groq API key and Firebase service account details. This file is not included in the repo for safety reasons.

```
python main.py
```

Frontend setup

Just open frontend/index.html in a browser for the citizen app, or frontend/dashboard.html for the authority dashboard. Make sure the API constant at the top of these files points to your backend URL.

## Note

This project was built for a hackathon in a short time, so some parts like Gemini API integration are still pending and can be added later. The core flow of reporting, AI categorization, tracking and resolving issues is fully working and live.
