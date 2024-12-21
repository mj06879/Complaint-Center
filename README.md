# Complaint Management System with Pairing Heap Algorithm

## Overview

This project showcases the application of the **Pairing Heap Algorithm** in managing user complaints. The system includes both a **User Interface** for complaint submission and an **Admin Interface** for managing and resolving complaints. Pairing heaps are used for efficient handling of the priority queue associated with complaints, allowing for the efficient retrieval and removal of the top complaints.

## Features

- **User Interface**:
  - Users can submit complaints related to various categories such as Personnel, Product/Service, Website, Delivery, and Communication.
  - Each complaint includes information such as the amount of the last purchase, product ID, purchase date, and a review.
  - Complaints are categorized through a dropdown menu for easy selection.

- **Admin Interface**:
  - Admins can view and manage the most recent complaints.
  - Admins have options to resolve complaints or recreate the heap for fresh data.
  - Admins can view the top complaints in real-time using a text box that updates automatically.

- **Pairing Heap Algorithm**:
  - The application uses the pairing heap algorithm to efficiently manage and retrieve the most recent and relevant complaints.
  - Pairing heaps provide an efficient way to handle priority queues in this complaint management system, making the retrieval and management of complaints quick and reliable.

## How to Run:

Download all these files and save them in a folder. Run the `main.py` file, making sure that you have the imported modules installed.

## Requirements

- Python 3.x
- Tkinter (for GUI)
- Pillow (for image handling)

To install the required libraries, run:

```bash
pip install tkinter pillow
```

