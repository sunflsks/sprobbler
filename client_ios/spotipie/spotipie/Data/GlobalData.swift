//
//  GlobalData.swift
//  spotipie
//
//  Created by Sudhip Nashi on 4/27/24.
//

import Foundation


struct GlobalData: Decodable {
    let ten_most_recent_scrobbles: [Scrobble]
    
    static func getGlobalData(base_url: URL) async throws -> GlobalData? {
        let (data, response) = try await URLSessionManager.normalSessionManager.data(from: URL(string: "/global", relativeTo: base_url) ?? URL(string: DEFAULT_URL)!)
        
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            return nil
        }
        
        return try JSONDecoder().decode(GlobalData.self, from: data)
    }
}
