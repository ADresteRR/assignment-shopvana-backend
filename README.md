# Shopvana Backend

This repository contains the backend code for the assignment (shopvana)
[backend-deployed-link](https://assignment-shopvana-backend-1.onrender.com)

## Table of Contents

- Introduction
- Technologies Used
- Setup
- API Endpoints

## Introduction

The backend service is responsible for handling all the API requests and managing the database for the Shopvana platform.

## Technologies Used

- Django
- PostgreSQL
- render (for hosting)

## Setup

To get this backend service running locally:

```sh
git clone https://your-backend-repository-link.git
cd your-backend-repository-directory
npm install
npm start
```
## API Endpoints

Below is a list of API endpoints provided by the Shopvana backend, along with their HTTP methods, a brief description, and the JSON objects required for the POST requests:

| Endpoint | HTTP Method | Description | JSON Object (if applicable) |
|----------|-------------|-------------|-----------------------------|
| `/get-user-id` | `GET` | Generates a temporary user ID for the session. | N/A |
| `/add-product` | `POST` | Adds a new product to the store. (Not available on UI, call explicitly) | `{"name": "Product Name", "description": "Product Description", "price": 0, "image": "${attach jpeg file}"}` |
| `/get-all-products` | `GET` | Retrieves all products available in the store. | N/A |
| `/get-all-options` | `GET` | Fetches all options for products. | N/A |
| `/add-option-list` | `POST` | Adds a list of options for a specific product. (Not available on UI, call explicitly) | `{"name": "optionsListName", "selection_type": "SINGLE" or "MULTIPLE" }` |
| `/add-options` | `POST` | Adds individual options to the product. (Not available on UI, call explicitly) | `{"name": "option name", "surcharge": "200", "option_list_id": "$id"}` |
| `/add-to-cart` | `POST` | Adds a product to the user's shopping cart. | N/A |
| `/remove-from-cart` | `POST` | Removes a product from the user's shopping cart. | N/A |
| `/get-cart-items/<str:temporary_user_id>` | `GET` | Retrieves all items in the cart for a given temporary user ID. | N/A |

*Note: Replace `<str:temporary_user_id>` with the actual temporary user ID to get the cart items for that user.*








