//
//  SongCellView.swift
//  spotipie
//
//  Created by Sudhip Nashi on 4/28/24.
//

import SwiftUI
import Kingfisher

struct GenericCell: View {
    @State var name: String
    @State var image_url: URL?
    @State var play_count: Int
    
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
        }
    }
}
