//
//  Song.swift
//  spotipie
//
//  Created by Sudhip Nashi on 5/5/24.
//

import Foundation

private let REMOTE_URL = "https://sprobbler.sudhip.com/info/album/"

struct Album: Decodable {
    struct SpotifyImageObject: Decodable {
        let url: URL
        let height: Int
        let width: Int
    }
    
    let id: String
        
    var images: [SpotifyImageObject]?
    var label: String?
    var name: String?
    var release_date: String?
    var total_tracks: Int?
    
    mutating func load() async throws {
        let (data, response) = try await URLSessionManager.cachedSessionManager.data(from: URL(string: REMOTE_URL + id)!)
        
        guard (response as! HTTPURLResponse).statusCode == 200 else {
            return
        }
        
        self = try JSONDecoder().decode(Album.self, from: data)
    }
}
