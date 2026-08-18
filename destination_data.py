
"""
Small, hand-curated destination corpus for the itinerary agent's FAISS
RAG store. This grounds the itinerary in real attractions instead of
letting the LLM invent an itinerary from pure memory (same hallucination
risk as the IATA code problem — this is the mitigation for it, applied
to a different part of the pipeline). Extend with more cities/chunks as
needed for your demo.
"""
 
DESTINATION_CONTENT = {
    "Goa": [
        "Baga Beach and Calangute Beach in North Goa are popular for water sports like parasailing and jet skiing, and have a lively nightlife scene with beach shacks and clubs.",
        "Old Goa is home to UNESCO World Heritage churches including the Basilica of Bom Jesus, which holds the remains of St. Francis Xavier.",
        "South Goa's Palolem and Agonda beaches are quieter and better for relaxing, with fewer crowds than the north.",
        "Dudhsagar Falls, a four-tiered waterfall on the Goa-Karnataka border, is a popular day-trip destination reachable by jeep safari through Bhagwan Mahavir Wildlife Sanctuary.",
        "Goan cuisine is known for seafood curries, pork vindaloo, and bebinca (a layered dessert); Fontainhas in Panaji is a Latin Quarter known for colorful Portuguese-era houses and cafes.",
    ],
    "Delhi": [
        "Red Fort and Jama Masjid in Old Delhi represent Mughal-era architecture; Chandni Chowk nearby is famous for street food and wholesale markets.",
        "India Gate and Rashtrapati Bhavan are in New Delhi, along with Humayun's Tomb, a precursor to the Taj Mahal's design.",
        "Qutub Minar, a UNESCO World Heritage 73-meter minaret, is one of Delhi's oldest monuments dating to the 12th century.",
        "Lotus Temple and Akshardham Temple are notable modern religious architecture sites, both offering peaceful gardens.",
        "Connaught Place is a central shopping and dining hub; Hauz Khas Village combines a medieval ruin with cafes and boutiques.",
    ],
    "Mumbai": [
        "Gateway of India and the nearby Taj Mahal Palace Hotel overlook the Arabian Sea and are Mumbai's most iconic landmarks.",
        "Marine Drive, a curved boulevard along the coast, is popular at sunset and known as the 'Queen's Necklace' for its streetlight pattern.",
        "Elephanta Caves, a UNESCO site with ancient rock-cut Hindu temples, is reachable by a one-hour ferry from Gateway of India.",
        "Chhatrapati Shivaji Maharaj Vastu Sangrahalaya (formerly Prince of Wales Museum) and the colonial-era Chhatrapati Shivaji Terminus railway station are architectural highlights.",
        "Bandra's Bandstand and Carter Road are popular seaside promenades; Mohammed Ali Road is known for its food during Ramadan.",
    ],
    "Bangalore": [
        "Lalbagh Botanical Garden and Cubbon Park are large green spaces in the city center, popular for morning walks.",
        "Bangalore Palace, built in Tudor-style architecture, and the Vidhana Soudha (state legislature building) are notable landmarks.",
        "The city is known as India's tech hub, with a strong pub and microbrewery culture concentrated around Indiranagar and Koramangala.",
        "ISKCON Temple and Bull Temple (Nandi Temple) are significant religious sites.",
        "Nandi Hills, about an hour outside the city, is a popular sunrise trekking and day-trip destination.",
    ],
    "Chennai": [
        "Marina Beach, one of the longest urban beaches in the world, is a major evening gathering spot.",
        "Kapaleeshwarar Temple in Mylapore is a classic example of Dravidian temple architecture.",
        "Fort St. George, built by the British East India Company, houses a museum with colonial-era artifacts.",
        "Mahabalipuram, about an hour south of the city, has UNESCO-listed rock-cut temples and shore temples from the 7th century Pallava dynasty.",
        "Chennai is known for Carnatic music and classical Bharatanatyam dance; the city hosts a major music season around December.",
    ],
}