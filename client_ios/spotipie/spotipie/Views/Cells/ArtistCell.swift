//
//  SongCellView.swift
//  spotipie
//
//  Created by Sudhip Nashi on 4/28/24.
//

import SwiftUI
import Kingfisher

struct ArtistCell : View {
    @State var name: String
    @State var image_url: URL?
    @State var play_count: Int
    @State var id: String
    
    let formatter = DateFormatter()
    
    var body: some View {
        HStack {
            KFImage(image_url)
                .resizable()
                .scaledToFit()
                .frame(width: 40, height: 40)
                .cornerRadius(5)
            
            VStack {
                HStack {
                    Text(name)
                    Spacer()
                }
                HStack {
                    Text("Play Count: " + String(play_count))
                    Spacer().font(.caption2)
                }
            }
        }.onAppear {
            Task {
                let (data, response) = try await URLSessionManager.cachedSessionManager.data(from: URL(string: "/info/artist/" + id, relativeTo: REMOTE_URL)!)
                
                guard (response as! HTTPURLResponse).statusCode == 200 else {
                    return
                }
                
                if let dict = try JSONSerialization.jsonObject(with: data) as? [String: Any] {
                    if let images = dict["images"] as? [[String: Any]] {
                        if let url_string = images[0]["url"] as? String {
                            self.image_url = URL(string: url_string)
                        }
                    }
                }
            }
        }
    }
}
