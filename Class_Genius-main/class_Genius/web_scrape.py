def get_resources(topic):
    return {
        "websites": [
            f"https://www.geeksforgeeks.org/{topic.replace(' ','-')}",
            f"https://www.tutorialspoint.com/{topic.replace(' ','_')}"
        ],
        "youtube": f"https://www.youtube.com/results?search_query={topic.replace(' ','+')}"
    }