//
//  Scrobble.swift
//  spotipie
//
//  Created by Sudhip Nashi on 03/08/24.
//

import Foundation

struct Scrobble: Decodable, Equatable {
    let name: String
    let played_at: Date
    let id: String
    let cover_image_url: URL?
}
