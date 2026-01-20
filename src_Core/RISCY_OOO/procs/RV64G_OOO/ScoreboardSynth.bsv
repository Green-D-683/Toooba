
// Copyright (c) 2017 Massachusetts Institute of Technology
// 
// Permission is hereby granted, free of charge, to any person
// obtaining a copy of this software and associated documentation
// files (the "Software"), to deal in the Software without
// restriction, including without limitation the rights to use, copy,
// modify, merge, publish, distribute, sublicense, and/or sell copies
// of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be
// included in all copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
// EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
// MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
// NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
// BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
// ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
// CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

`include "ProcConfig.bsv"
import Scoreboard::*;
import SynthParam::*;


`ifdef SUPERSCALAR

    // conservative sb
    typedef RenamingScoreboard#(WrConsPortNum, SbLazyLookupPortNum) ScoreboardCons;

    (* synthesize *)
    module mkScoreboardCons(ScoreboardCons);
        let m <- mkRenamingScoreboard;
        return m;
    endmodule

    // aggressive sb
    typedef RenamingScoreboard#(WrAggrPortNum, 0) ScoreboardAggr;

    (* synthesize *)
    module mkScoreboardAggr(ScoreboardAggr);
        let m <- mkRenamingScoreboard;
        return m;
    endmodule

`else // IN_ORDER

    typedef InorderRenamingScoreboard#(WrConsPortNum, SbLazyLookupPortNum) ScoreboardInOrder;

    (* synthesize *)
    module mkScoreboardInOrder(ScoreboardInOrder);
        let m <- mkInorderRenamingScoreboard;
        return m;
    endmodule

`endif

/*
# Regular Scoreboard:

interface RenamingScoreboard#(numeric type setReadyNum, numeric type lazyLookupNum);
    // eager look up when insert to reservation station, must see setReady & previous setBusy effects
    interface Vector#(SupSize, SbLookup) eagerLookup;
    interface Vector#(SupSize, SbSetBusy) setBusy;
    interface Vector#(setReadyNum, Put#(PhyRIndx)) setReady;
    // lazy look up in reg read, no need to see setReady effect (reg read rule will check bypass)
    interface Vector#(lazyLookupNum, SbLookup) lazyLookup;
endinterface

// BYPASS scoreboard to use with register renaming in an in-order core
// setReady < lookup < setBusy
interface InorderRenamingScoreboard#(
    numeric type setReadyNum, numeric type lookupNum
);
    interface Vector#(lookupNum, SbLookup) lookup; // together with RF read
    interface Vector#(SupSize, SbSetBusy) setBusy; // at rename
    interface Vector#(setReadyNum, Put#(PhyRIndx)) setReady; // exe finishes
endinterface

 */


