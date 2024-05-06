//
//  Song.swift
//  spotipie
//
//  Created by Sudhip Nashi on 5/5/24.
//

import Foundation

private let REMOTE_URL = "https://sprobbler.sudhip.com/info/track/"

struct Song: Decodable {
    let track_id: String
    var song_details: SongDetails?
    
    struct SongDetails: Decodable {
        let name: String
        let duration_ms: UInt32
        
        let is_local: Bool
        let preview_url: URL
        let explicit: Bool?
    }
    
    mutating func load() async throws {
        let urlRequest = URLRequest(url: URL(string: REMOTE_URL + track_id)!)
        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        
        guard (response as! HTTPURLResponse).statusCode == 200 else {
            return
        }
        
        try song_details = JSONDecoder().decode(SongDetails.self, from: data)
    }
}
