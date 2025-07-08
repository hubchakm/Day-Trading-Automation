CXX=g++
CXXFLAGS=-std=c++17 -Wall -Iinclude
LDFLAGS=-lcurl
SRC=$(wildcard src/*.cpp)
OBJ=$(SRC:.cpp=.o)
TARGET=trader

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CXX) $(OBJ) -o $@ $(LDFLAGS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f src/*.o $(TARGET)

.PHONY: all clean
