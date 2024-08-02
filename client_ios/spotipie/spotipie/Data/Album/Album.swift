//
//  Song.swift
//  spotipie
//
//  Created by Sudhip Nashi on 5/5/24.
//

import Foundation


struct Album: Decodable {
    struct SpotifyImageObject: Decodable {
        let url: URL
        let height: Int
        let width: Int
    }
    
    struct AlbumTrackInfo: Decodable {
        struct Track: Decodable {
            let name: String
            let id: String
        }
        
        let items: [Track]
    }

    let id: String
        
    var images: [SpotifyImageObject]?
    var label: String?
    var name: String?
    var release_date: String?
    var total_tracks: Int?
    var tracks: AlbumTrackInfo?
    
    mutating func load(base_url: URL) async throws {
        let (data, response) = try await URLSessionManager.cachedSessionManager.data(from: URL(string: "/info/album/" + id, relativeTo: base_url) ?? URL(string: DEFAULT_URL)!)
        
        guard (response as! HTTPURLResponse).statusCode == 200 else {
            return
        }
        
        self = try JSONDecoder().decode(Album.self, from: data)
    }
}
