# Traffic Prediction from LTA Data
Currently a work in progress! This is a project for DSA3101 (Data Science in Practice)
Project by: @MingFengC @renachongpq @acakebro @RebeccaWam

## Background
Based on traffic images, speedbands and incidents obtained from [LTA Datamall](https://datamall.lta.gov.sg/content/datamall/en/dynamic-data.html), we estimate the traffic density for live data and predict if there is a jam on a particular road

## Workflow Overview
1. Making API calls to obtain traffic images, speedbands and incidents
2. Selecting ROI for Traffic Images
3. Vehicle Detection & Counting for Traffic Images
4. Model for Traffic Prediction
