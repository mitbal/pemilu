pemilu
======

Indonesia President Election 2014: A Machine Learning Approach

This is an attempt to create handwritten digits dataset by extracting digit sub-image from scanned C1 images and class label that is annotated by using crowdsourcing.
Furthermore experiment with many machine learning techniques and methods from the said dataset.

The important modules are:

## scrap.py
-----------
Download the scanned C1 images from KPU (Indonesia election committe) server and crowdsourced annotation from kawalpemilu.org

## extract.py
-------------
Extract the digit image from the scanned image

## gui-tk.py
------------
Graphical user interface to interact by loading a scanned image and extract the vote count using pre-trained model

## visualize.py
---------------
Visualize subset of dataset images
