//
//  Song.swift
//  spotipie
//
//  Created by Sudhip Nashi on 5/5/24.
//

import Foundation

struct Song: Decodable {
    let id: String
    var name: String?
    var duration_ms: UInt32?
    
    var is_local: Bool?
    var preview_url: URL?
    var explicit: Bool?
    var predicted_genres: [String]?
    
    var album: Album?
    
    mutating func load(base_url: URL) async throws {
        let (data, response) = try await URLSessionManager.cachedSessionManager.data(from: URL(string:  "/info/track/" + id, relativeTo: base_url) ?? URL(string: DEFAULT_URL)! )
        
        guard (response as! HTTPURLResponse).statusCode == 200 else {
            return
        }
        
        self = try JSONDecoder().decode(Song.self, from: data)
    }
}
