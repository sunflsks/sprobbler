//
//  GlobalData.swift
//  spotipie
//
//  Created by Sudhip Nashi on 4/27/24.
//

import Foundation


struct GlobalData: Decodable {
    struct PlayedItem: Decodable {
        let name: String
        let play_count: Int
        let cover_image_url: URL?
        let id: String
    }
    
    struct Scrobble: Decodable, Equatable {
        let name: String
        let played_at: String
        let id: String
        let cover_image_url: URL?
    }
   
    let ten_most_recent_scrobbles: [Scrobble]
    let ten_most_played_artists: [PlayedItem]
    let ten_most_played_albums: [PlayedItem]
    let ten_most_played_tracks: [PlayedItem]
    
    static func getGlobalData(base_url: URL) async throws -> GlobalData? {
        let (data, response) = try await URLSessionManager.normalSessionManager.data(from: URL(string: "/global", relativeTo: base_url) ?? URL(string: DEFAULT_URL)!)
        
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            return nil
        }
        
        return try JSONDecoder().decode(GlobalData.self, from: data)
    }
}
