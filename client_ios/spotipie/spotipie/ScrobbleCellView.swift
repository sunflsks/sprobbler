//
//  SongCellView.swift
//  spotipie
//
//  Created by Sudhip Nashi on 4/28/24.
//

import SwiftUI
import Kingfisher

struct ScrobbleCellView: View {
    @State var name: String
    @State var played_at: Date?
    @State var image_url: URL?
    
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
                    Text(dateToString(date: played_at ?? Date.now))
                    Spacer().font(.caption2)
                }
            }
        }
    }
}
