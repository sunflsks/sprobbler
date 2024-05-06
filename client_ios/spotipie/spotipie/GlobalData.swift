//
//  GlobalData.swift
//  spotipie
//
//  Created by Sudhip Nashi on 4/27/24.
//

import Foundation

private let REMOTE_URL = "https://sprobbler.sudhip.com/global"

struct GlobalData: Decodable {
    struct PlayedItem: Decodable {
        let name: String
        let play_count: Int
        let cover_image_url: URL?
    }
    
    struct Scrobble: Decodable {
        let name: String
        let played_at: String
        let track_id: String
        let cover_image_url: URL?
    }
   
    let ten_most_recent_scrobbles: [Scrobble]
    let ten_most_played_artists: [PlayedItem]
    let ten_most_played_albums: [PlayedItem]
    let ten_most_played_tracks: [PlayedItem]
    
    static func getGlobalData() async throws -> GlobalData? {
        let urlRequest = URLRequest(url: URL(string: REMOTE_URL)!)
        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            return nil
        }
        
        return try JSONDecoder().decode(GlobalData.self, from: data)
    }
}
