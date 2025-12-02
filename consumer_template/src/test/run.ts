import { handler } from "..";
let event = {
    path: "/",
    headers: {
        "Content-Type": "docType",
        "Producer-Key": "producerKey",
        "Consumer-Key": "edw_rmsReplenishment_consumer",
        "Native-Business-Id": "134",
        "Document-Key": "343e838e-d579-401f-8c29-edc29fe26d26"
    },
    body: JSON.stringify({ title: 'New Product', price: 29.99 })
}
handler(event, {})


/* {
        "companyId": "SGNT123",
        "sku": "SGNT-12345",
        "productPageUrl": "https://example.com/product123",
        "productPageLanguage": "eng",
        "imageUrl": "https://example.com/images/product123.jpg",
        "name": "Elegant Diamond Ring",
        "description": "A stunning diamond ring with intricate design",
        "metalType": "Platinum",
        "metalColor": "White",
        "metalKarat": "18K",
        "length": "6.5 inches",
        "size": "Medium",
        "diamondWeight": "1.25 carats",
        "stoneType": "diamond",
        "diamondClarity": "clear",
        "diamondColor": "white",
        "stoneNumber": "2",
        "secondaryStoneType": "emerald",
        "weight": "1.25 carats",
        "fill": "solid",
        "diameter": "15 mm",
        "productCollection": "Elegant Collection",
        "onlineExclusive": "true",
        "additionalAttributes": "Diamond Color Rating Code: H-I",
        "recordStatus": "A",
        "lastUpdateTime": "2024-04-10T15:30:00Z"
    } */