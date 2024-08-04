//
//  PlayedItem.swift
//  spotipie
//
//  Created by Sudhip Nashi on 03/08/24.
//

import Foundation

struct PlayedItem: Decodable {
    let name: String
    let play_count: Int
    let cover_image_url: URL?
    let id: String
}
