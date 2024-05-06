//
//  Song.swift
//  spotipie
//
//  Created by Sudhip Nashi on 5/5/24.
//

import Foundation

private let REMOTE_URL = "https://sprobbler.sudhip.com/info/track/"

struct Song: Decodable {
    let id: String
    var name: String?
    var duration_ms: UInt32?
    
    var is_local: Bool?
    var preview_url: URL?
    var explicit: Bool?
    
    var album: Album?
    
    mutating func load() async throws {
        let (data, response) = try await URLSessionManager.cachedSessionManager.data(from: URL(string: REMOTE_URL + id)!)
        
        guard (response as! HTTPURLResponse).statusCode == 200 else {
            return
        }
        
        self = try JSONDecoder().decode(Song.self, from: data)
    }
}
