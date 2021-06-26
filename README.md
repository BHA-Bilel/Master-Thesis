# Master-Thesis 👨‍🎓 "Question-Answering System for automatic response of islamic fatwas questions"
This repository contains the web app I created using Flask, as an additional (individual) effort outside the goals defined by the thesis, that was destined for the general public.

> Before even making this web app, I trained some classification models using Scikit-learn library, and semantic similarity calculation model using gensim's Doc2Vec.
>
> This repository wouldn't exist if not for **Corey Schafer**'s amazing [Flask tutorials](https://www.youtube.com/playlist?list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH) that paved my path to learn, I totally recommend it
>
> You can download my master's thesis [here](./thesis/thesis.pdf?raw=true) (written in french)

## Table of contents
* [Features](#features)
* [Project Status](#project-status)
* [Thesis Abstract](#thesis-abstract)

# Features

- bootstrap: graphically pleasing UI without a hassle for a junior web dev like me
- flask-login: Authentification and User Priviledges (Hierarchical User Types)
- flask-admin: in-production models training/exportation, corpus importation/exportation
- flask-mail: Email Verification, Password Reset and Automated Email Notifications
- flask-sqlalchemy: to interact with the database using an ORM
- flask-babel: to support multiple languages

# Project Status

The web app is NOT production ready for the following reasons:

- First off Fatwas are of great importance in Islam, it's a whole branch in the Islamic religion and cannot be given by any scholar
- The Fatwas was collected for a related previous work, that has no proper author attribution
- Due to COVID-19 lockdowns I couldn't manage to reach domain experts (muftis) to assist me

That being said, I would definitely complete and launch the project under the right circumstances

# Thesis Abstract

Most of the questions asked about Islamic Sharia (otherwise known as “Fatwa’s demands”) have already been answered by the Muftis over time. Given the difficulty of contacting Muftis directly for immediate and adequate answers to specific questions, the intelligent use of previous Fatwas seems a very good solution. On the other hand, Muftis in several situations repeat the same Fatwas for similar questions.

The goal of this research is to surpass that repetition by implementing a system which automatically answers Fatwas questions asked by muslims during an exchange of arabic natural language.

The task of that system is to classify the question in its topic and search for similar questions in a database using artificial intelligence models, in order to provide an answer to the question.

Several systems were implemented in this domain, using various question answering paradigms, but only two of them used machine learning approach.
Artificial intelligence models are capable of providing instant and very accurate results without the need of any human intervention.

Besides using machine learning models, this work is the first one to use a deep learning model in the domain of fatwas question answering systems (as far as we know).

The proposed approach is composed of two main modules, a first concerns the routing of Fatwa requests in the appropriate categories of the Chriaa and the second responds concretely to the request by doing a search based on semantic similarity in existing databases
