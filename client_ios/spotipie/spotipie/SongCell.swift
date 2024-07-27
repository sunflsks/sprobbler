//
//  SongCellView.swift
//  spotipie
//
//  Created by Sudhip Nashi on 4/28/24.
//

import SwiftUI
import Kingfisher

struct SongCell: View {
    @State var name: String
    
    let formatter = DateFormatter()
    
    var body: some View {
        HStack {
            VStack {
                HStack {
                    Text(name)
                    Spacer()
                }
            }
        }
    }
}
